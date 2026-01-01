import { useState, useEffect, useCallback } from 'react'
import { Music, Plus, X, Upload, Play, FolderOpen, Pause, XCircle, Disc3, Download, RotateCcw } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { api } from '../lib/api'

export default function InstrumentalMaker() {
  const [urls, setUrls] = useState([''])
  const [uploadedFile, setUploadedFile] = useState(null)
  const [isDragging, setIsDragging] = useState(false)

  // Processing state
  const [isProcessing, setIsProcessing] = useState(false)
  const [jobId, setJobId] = useState(null)
  const [progress, setProgress] = useState(0)
  const [currentVideo, setCurrentVideo] = useState(0)
  const [totalVideos, setTotalVideos] = useState(0)
  const [statusMessage, setStatusMessage] = useState('')
  const [results, setResults] = useState([])

  // Audio player state
  const [playingId, setPlayingId] = useState(null)
  const [playingType, setPlayingType] = useState(null) // 'instrumental' or 'acapella'
  const [audioElement, setAudioElement] = useState(null)

  // Progress estimation state
  const [estimatedProgress, setEstimatedProgress] = useState(0)
  const [lastVideoStartTime, setLastVideoStartTime] = useState(null)
  const [avgVideoTime, setAvgVideoTime] = useState(180000) // Default 3 minutes

  // Estimate progress based on time elapsed
  useEffect(() => {
    if (!isProcessing || !lastVideoStartTime) return

    const interval = setInterval(() => {
      const elapsed = Date.now() - lastVideoStartTime
      const estimatedPercentage = Math.min((elapsed / avgVideoTime) * 100, 99)
      setEstimatedProgress(estimatedPercentage)
    }, 500) // Update every 500ms for smooth animation

    return () => clearInterval(interval)
  }, [isProcessing, lastVideoStartTime, avgVideoTime])

  // Poll for job status
  useEffect(() => {
    if (!jobId) return

    console.log('Starting status polling for job:', jobId)

    const interval = setInterval(async () => {
      try {
        const status = await api.getJobStatus(jobId)

        console.log('Job status:', status)

        setCurrentVideo(status.current_video)
        setTotalVideos(status.total_videos)
        setStatusMessage(status.message)

        // Detect when a new video starts processing
        if (status.current_video !== currentVideo && status.current_video > 0) {
          const now = Date.now()

          // Calculate time taken for previous video
          if (lastVideoStartTime) {
            const timeTaken = now - lastVideoStartTime
            // Update average time (weighted average)
            setAvgVideoTime(prev => (prev * 0.7) + (timeTaken * 0.3))
          }

          setLastVideoStartTime(now)
          setEstimatedProgress(0)
        }

        if (status.status === 'complete' || status.status === 'completed' || status.status === 'failed') {
          console.log('Job completed! Setting results:', status.results)
          setIsProcessing(false)
          setResults(status.results || [])
          setProgress(100)
          setEstimatedProgress(100)
          clearInterval(interval)
        } else {
          // Use estimated progress capped at 99%
          setProgress(estimatedProgress)
        }
      } catch (error) {
        console.error('Error polling status:', error)

        // If we get a 404 (job not found), the server likely restarted
        // Clear the job state to allow user to start fresh
        if (error.message && error.message.includes('Job not found')) {
          console.log('Job not found - server may have restarted. Clearing job state.')
          setIsProcessing(false)
          setJobId(null)
          setProgress(0)
          setCurrentVideo(0)
          setTotalVideos(0)
          setStatusMessage('Server restarted. Please submit a new request.')
          clearInterval(interval)
        }
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [jobId])

  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setIsDragging(false)

    const files = e.dataTransfer.files
    if (files.length > 0 && files[0].type.startsWith('audio/')) {
      setUploadedFile(files[0])
    }
  }, [])

  const handleFileSelect = (e) => {
    const files = e.target.files
    if (files.length > 0) {
      setUploadedFile(files[0])
    }
  }

  const addUrlField = () => {
    setUrls([...urls, ''])
  }

  const removeUrlField = (index) => {
    const newUrls = urls.filter((_, i) => i !== index)
    setUrls(newUrls.length > 0 ? newUrls : [''])
  }

  const updateUrl = (index, value) => {
    const newUrls = [...urls]
    newUrls[index] = value
    setUrls(newUrls)
  }

  const handleProcess = async () => {
    // Validate inputs
    const hasUrls = urls.some(url => url.trim())
    const hasFile = uploadedFile !== null

    if (!hasUrls && !hasFile) {
      alert('Please provide at least one YouTube URL or upload an audio file')
      return
    }

    setIsProcessing(true)
    setProgress(0)
    setResults([])
    setEstimatedProgress(0)
    setLastVideoStartTime(Date.now()) // Start timing immediately

    try {
      let response

      if (hasFile) {
        // Upload file processing
        const formData = new FormData()
        formData.append('audio', uploadedFile)
        response = await api.processAudioFile(formData)
      } else {
        // YouTube processing - instrumental only (no video)
        const payload = {
          video_urls: urls.filter(url => url.trim()),
          create_video: false,
          save_locally: true,
          upload_to_youtube: false
        }
        response = await api.processInstrumental(payload)
      }

      setJobId(response.job_id)
    } catch (error) {
      console.error('Error processing:', error)
      alert('Failed to start processing: ' + error.message)
      setIsProcessing(false)
    }
  }

  const playAudio = (filePath, resultId, type) => {
    if (playingId === resultId && playingType === type) {
      // Pause current audio
      if (audioElement) {
        audioElement.pause()
        setPlayingId(null)
        setPlayingType(null)
      }
    } else {
      // Stop previous audio
      if (audioElement) {
        audioElement.pause()
      }

      // Play new audio - prepend backend URL if path starts with /
      const audioUrl = filePath.startsWith('/')
        ? `http://localhost:5000${filePath}`
        : filePath
      const audio = new Audio(audioUrl)
      audio.play()
      setAudioElement(audio)
      setPlayingId(resultId)
      setPlayingType(type)

      audio.onended = () => {
        setPlayingId(null)
        setPlayingType(null)
      }
    }
  }

  const downloadAudio = (filePath, filename) => {
    // Create a link element and trigger download
    const audioUrl = filePath.startsWith('/')
      ? `http://localhost:5000${filePath}?download=true`
      : filePath
    const link = document.createElement('a')
    link.href = audioUrl
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const openFileLocation = (filePath) => {
    // This would need a backend endpoint to open the file location
    api.openFileLocation(filePath)
  }

  const handleCancel = async () => {
    if (!jobId) return

    // If job is complete, just reset without confirmation
    const isComplete = progress === 100 || results.length > 0

    if (!isComplete && !confirm('Are you sure you want to cancel this job?')) return

    try {
      // Only call cancel API if job is still processing
      if (!isComplete) {
        await api.cancelJob(jobId)
      }

      // Reset all state
      setIsProcessing(false)
      setJobId(null)
      setProgress(0)
      setCurrentVideo(0)
      setTotalVideos(0)
      setStatusMessage('')
      setResults([])
    } catch (error) {
      console.error('Error cancelling job:', error)
      alert('Failed to cancel job: ' + error.message)
    }
  }

  return (
    <div className="flex-1 flex flex-col">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 min-h-[calc(100vh-400px)]">
        {/* Left Column - Input */}
        <motion.div
          className="flex flex-col space-y-6 h-full"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          {/* YouTube Videos */}
          <div className="card-retro flex-[1] flex flex-col justify-center">
            <div className="flex items-center justify-between mb-6">
              <h3 className="label-retro mb-0">YOUTUBE VIDEOS</h3>
              <button
                onClick={addUrlField}
                className="btn-retro btn-secondary text-xs px-3 py-1 flex items-center gap-1"
                disabled={isProcessing}
              >
                <Plus className="w-3 h-3" />
                ADD MORE
              </button>
            </div>

            <div className="space-y-4">
              {urls.map((url, index) => (
                <div key={index} className="flex gap-2">
                  <input
                    type="text"
                    className="input-retro flex-1"
                    value={url}
                    onChange={(e) => updateUrl(index, e.target.value)}
                    placeholder="https://www.youtube.com/watch?v=..."
                    disabled={isProcessing}
                  />
                  {urls.length > 1 && (
                    <button
                      onClick={() => removeUrlField(index)}
                      className="btn-retro btn-danger text-xs px-3"
                      disabled={isProcessing}
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* File Upload */}
          <div className="card-retro flex-[2] flex flex-col justify-center">
            <h3 className="label-retro mb-6">OR UPLOAD AUDIO FILE</h3>

            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`
                border-4 border-dashed rounded-retro-lg p-12 min-h-[280px] flex items-center justify-center text-center transition-all cursor-pointer
                ${isDragging
                  ? 'border-retro-orange bg-retro-orange/10'
                  : 'border-retro-gold/30 hover:border-retro-gold/50 hover:bg-[#3d2817]/20'
                }
              `}
              onClick={() => document.getElementById('audio-input').click()}
            >
              <input
                id="audio-input"
                type="file"
                accept="audio/*"
                onChange={handleFileSelect}
                className="hidden"
                disabled={isProcessing}
              />

              {uploadedFile ? (
                <div className="space-y-2">
                  <Music className="w-12 h-12 text-retro-gold mx-auto" />
                  <div className="text-retro-cream font-retro font-bold">{uploadedFile.name}</div>
                  <div className="text-retro-mustard text-sm font-retro">
                    {(uploadedFile.size / (1024 * 1024)).toFixed(1)} MB
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      setUploadedFile(null)
                    }}
                    className="btn-retro btn-danger text-xs mt-2"
                    disabled={isProcessing}
                  >
                    Remove
                  </button>
                </div>
              ) : (
                <div className="space-y-6">
                  <Upload className="w-20 h-20 text-retro-gold/50 mx-auto" />
                  <div className="text-retro-cream font-retro text-lg">
                    Drop audio file here or click to browse
                  </div>
                  <div className="text-retro-mustard text-sm font-retro">
                    Supports MP3, WAV, FLAC, and more
                  </div>
                </div>
              )}
            </div>
          </div>
        </motion.div>

        {/* Right Column - Ready State, Processing & Results */}
        <motion.div
          className="flex flex-col h-full"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
        >
          {/* Empty State / Ready / Processing */}
          {results.length === 0 && (
            <div className="flex flex-col h-full justify-between gap-6">
              <div className="card-retro flex-1">
                <div className="glass-retro p-12 text-center h-full flex flex-col items-center justify-center gap-6">
                  {isProcessing ? (
                    <div className="flex flex-col items-center gap-6">
                      <motion.div
                        className="relative"
                        animate={{ rotate: 360 }}
                        transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
                      >
                        <Disc3 className="w-32 h-32 text-retro-gold" />
                        <div className="absolute inset-0 bg-retro-orange/20 rounded-full blur-xl"></div>
                      </motion.div>
                      <div className="space-y-2">
                        <h3 className="text-retro-gold font-display text-2xl">PROCESSING</h3>
                        <p className="text-retro-mustard font-retro text-sm">
                          This may take a few minutes
                        </p>
                        {statusMessage && (
                          <p className="text-retro-sage font-retro text-xs">
                            {statusMessage}
                          </p>
                        )}
                      </div>
                    </div>
                  ) : (urls.some(url => url.trim()) || uploadedFile) ? (
                    <button
                      onClick={handleProcess}
                      disabled={isProcessing}
                      className="btn-retro btn-secondary text-2xl px-12 py-6 flex items-center gap-4"
                    >
                      <Music className="w-8 h-8" />
                      CONVERT
                    </button>
                  ) : (
                    <motion.div
                      animate={{ scale: [1, 1.1, 1] }}
                      transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                    >
                      <Music className="w-32 h-32 text-retro-gold/50" />
                    </motion.div>
                  )}
                </div>
              </div>

            </div>
          )}

          {/* Results Only */}
          <AnimatePresence>
            {results.length > 0 && (
              <motion.div
                className="space-y-6"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                {/* Results */}
                <div className="card-retro">
                  <h3 className="label-retro mb-4">PROCESSING</h3>

                  <div className="space-y-4">
                    {/* VU Meter Style Progress */}
                    <div className="progress-retro">
                      <div
                        className="progress-retro-fill"
                        style={{ width: `${progress}%` }}
                      />
                    </div>

                    <div className="flex justify-between text-retro-cream font-retro text-sm">
                      <span>PROGRESS:</span>
                      <span className="text-retro-gold">{Math.round(progress)}%</span>
                    </div>

                    {totalVideos > 0 && (
                      <div className="flex justify-between text-retro-mustard font-retro text-sm">
                        <span>VIDEO:</span>
                        <span>{currentVideo} / {totalVideos}</span>
                      </div>
                    )}

                    {/* First video notice */}
                    {currentVideo === 1 && totalVideos > 1 && (
                      <div className="glass-retro p-3 rounded-retro border-2 border-retro-mustard/30">
                        <p className="text-retro-mustard font-retro text-xs text-center">
                          Progress estimation will improve after first video completes
                        </p>
                      </div>
                    )}

                    {statusMessage && (
                      <div className="glass-retro p-3 rounded-retro">
                        <p className="text-retro-cream font-retro text-sm">{statusMessage}</p>
                      </div>
                    )}

                    {/* Cancel/Reset Button */}
                    <button
                      onClick={handleCancel}
                      className={`btn-retro w-full flex items-center justify-center gap-2 ${
                        progress === 100 || results.length > 0 ? 'btn-secondary' : 'btn-danger'
                      }`}
                    >
                      {progress === 100 || results.length > 0 ? (
                        <>
                          <RotateCcw className="w-5 h-5" />
                          RESET
                        </>
                      ) : (
                        <>
                          <XCircle className="w-5 h-5" />
                          CANCEL JOB
                        </>
                      )}
                    </button>
                  </div>
                </div>

                {/* Results */}
                {results.length > 0 && (
                  <div className="card-retro">
                    <h3 className="label-retro mb-4">COMPLETED ({results.length})</h3>

                    <div className="space-y-3 max-h-[600px] overflow-y-auto">
                      {results.map((result, index) => (
                        <motion.div
                          key={index}
                          className="p-4 bg-[#3d2817]/30 rounded-retro border-2 border-retro-gold/20"
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.1 }}
                        >
                          <div className="space-y-3">
                            <div className="text-retro-cream font-retro font-bold truncate">
                              {result.title || result.filename}
                            </div>

                            {/* Instrumental Player */}
                            {result.instrumental && (
                              <div className="space-y-2">
                                <div className="text-retro-sage text-xs font-retro">INSTRUMENTAL</div>
                                <div className="flex gap-2">
                                  <button
                                    onClick={() => playAudio(result.instrumental, index, 'instrumental')}
                                    className="btn-retro btn-secondary text-xs px-3 py-2 flex-1 flex items-center justify-center gap-2"
                                  >
                                    {playingId === index && playingType === 'instrumental' ? (
                                      <>
                                        <Pause className="w-4 h-4" />
                                        PAUSE
                                      </>
                                    ) : (
                                      <>
                                        <Play className="w-4 h-4" />
                                        PLAY
                                      </>
                                    )}
                                  </button>
                                  <button
                                    onClick={() => downloadAudio(result.instrumental, `${result.title} - Instrumental.mp3`)}
                                    className="btn-retro btn-primary text-xs px-3 py-2 flex items-center justify-center gap-2"
                                  >
                                    <Download className="w-4 h-4" />
                                    DOWNLOAD
                                  </button>
                                </div>
                              </div>
                            )}

                            {/* Acapella Player */}
                            {result.acapella && (
                              <div className="space-y-2">
                                <div className="text-retro-sage text-xs font-retro">ACAPELLA</div>
                                <div className="flex gap-2">
                                  <button
                                    onClick={() => playAudio(result.acapella, index, 'acapella')}
                                    className="btn-retro btn-secondary text-xs px-3 py-2 flex-1 flex items-center justify-center gap-2"
                                  >
                                    {playingId === index && playingType === 'acapella' ? (
                                      <>
                                        <Pause className="w-4 h-4" />
                                        PAUSE
                                      </>
                                    ) : (
                                      <>
                                        <Play className="w-4 h-4" />
                                        PLAY
                                      </>
                                    )}
                                  </button>
                                  <button
                                    onClick={() => downloadAudio(result.acapella, `${result.title} - Acapella.mp3`)}
                                    className="btn-retro btn-primary text-xs px-3 py-2 flex items-center justify-center gap-2"
                                  >
                                    <Download className="w-4 h-4" />
                                    DOWNLOAD
                                  </button>
                                </div>
                              </div>
                            )}

                            {/* Fallback for old output_path format */}
                            {!result.instrumental && !result.acapella && result.output_path && (
                              <div className="flex gap-2">
                                <button
                                  onClick={() => playAudio(result.output_path, index, 'instrumental')}
                                  className="btn-retro btn-secondary text-xs px-4 py-2 flex-1 flex items-center justify-center gap-2"
                                >
                                  {playingId === index ? (
                                    <>
                                      <Pause className="w-4 h-4" />
                                      PAUSE
                                    </>
                                  ) : (
                                    <>
                                      <Play className="w-4 h-4" />
                                      PLAY
                                    </>
                                  )}
                                </button>
                                <button
                                  onClick={() => openFileLocation(result.output_path)}
                                  className="btn-retro btn-primary text-xs px-4 py-2 flex-1 flex items-center justify-center gap-2"
                                >
                                  <FolderOpen className="w-4 h-4" />
                                  GO TO FILE
                                </button>
                              </div>
                            )}
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </div>
  )
}
