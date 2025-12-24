import { useState, useCallback } from 'react'
import { Upload, FileVideo, Sparkles, Hash, FileText, Eye, Send } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { api } from '../lib/api'

export default function YouTubeUploader() {
  const [videoFile, setVideoFile] = useState(null)
  const [isDragging, setIsDragging] = useState(false)

  // AI Metadata Controls
  const [titleInput, setTitleInput] = useState('')
  const [descriptionInput, setDescriptionInput] = useState('')
  const [descriptionStyle, setDescriptionStyle] = useState('balanced') // minimal, balanced, detailed
  const [tagCount, setTagCount] = useState(5)

  // Generated Metadata
  const [generatedTitle, setGeneratedTitle] = useState('')
  const [generatedDescription, setGeneratedDescription] = useState('')
  const [generatedTags, setGeneratedTags] = useState([])
  const [isGenerating, setIsGenerating] = useState(false)

  // Upload State
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadResult, setUploadResult] = useState(null)

  // Privacy
  const [privacyStatus, setPrivacyStatus] = useState('public')

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
    if (files.length > 0 && files[0].type.startsWith('video/')) {
      setVideoFile(files[0])
    }
  }, [])

  const handleFileSelect = (e) => {
    const files = e.target.files
    if (files.length > 0) {
      setVideoFile(files[0])
    }
  }

  const generateMetadata = async () => {
    if (!titleInput.trim()) {
      alert('Please enter a title summary (1-2 sentences)')
      return
    }

    setIsGenerating(true)

    try {
      const response = await api.optimizeSEO({
        title_summary: titleInput,
        description_brief: descriptionInput || titleInput,
        description_style: descriptionStyle,
        tag_count: tagCount
      })

      setGeneratedTitle(response.title)
      setGeneratedDescription(response.description)
      setGeneratedTags(response.tags)
    } catch (error) {
      console.error('Error generating metadata:', error)
      alert('Failed to generate metadata: ' + error.message)
    } finally {
      setIsGenerating(false)
    }
  }

  const handleUpload = async () => {
    if (!videoFile) {
      alert('Please select a video file')
      return
    }

    if (!generatedTitle) {
      alert('Please generate metadata first')
      return
    }

    setIsUploading(true)
    setUploadProgress(0)

    try {
      const formData = new FormData()
      formData.append('video', videoFile)
      formData.append('title', generatedTitle)
      formData.append('description', generatedDescription)
      formData.append('tags', JSON.stringify(generatedTags))
      formData.append('privacy_status', privacyStatus)

      const response = await api.uploadVideo(formData)
      setUploadResult(response)
      setUploadProgress(100)
    } catch (error) {
      console.error('Error uploading:', error)
      alert('Upload failed: ' + error.message)
    } finally {
      setIsUploading(false)
    }
  }

  const resetForm = () => {
    setVideoFile(null)
    setTitleInput('')
    setDescriptionInput('')
    setGeneratedTitle('')
    setGeneratedDescription('')
    setGeneratedTags([])
    setUploadResult(null)
    setUploadProgress(0)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card-retro">
        <div className="flex items-center gap-3 mb-2">
          <Upload className="w-8 h-8 text-retro-gold" />
          <div>
            <h2 className="font-display text-3xl text-retro-gold">YOUTUBE UPLOADER</h2>
            <p className="text-retro-mustard font-retro text-sm">Upload videos with AI-generated metadata</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column - File Upload */}
        <motion.div
          className="space-y-6"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          {/* File Drop Zone */}
          <div className="card-retro">
            <h3 className="label-retro mb-4">
              <FileVideo className="inline w-5 h-5 mr-2" />
              VIDEO FILE
            </h3>

            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`
                border-4 border-dashed rounded-retro-lg p-12 text-center transition-all cursor-pointer
                ${isDragging
                  ? 'border-retro-orange bg-retro-orange/10'
                  : 'border-retro-gold/30 hover:border-retro-gold/50 hover:bg-[#3d2817]/20'
                }
              `}
              onClick={() => document.getElementById('file-input').click()}
            >
              <input
                id="file-input"
                type="file"
                accept="video/*"
                onChange={handleFileSelect}
                className="hidden"
                disabled={isUploading}
              />

              {videoFile ? (
                <div className="space-y-3">
                  <FileVideo className="w-16 h-16 text-retro-gold mx-auto" />
                  <div className="text-retro-cream font-retro font-bold">{videoFile.name}</div>
                  <div className="text-retro-mustard text-sm font-retro">
                    {(videoFile.size / (1024 * 1024)).toFixed(1)} MB
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      setVideoFile(null)
                    }}
                    className="btn-retro btn-danger text-xs mt-2"
                    disabled={isUploading}
                  >
                    Remove
                  </button>
                </div>
              ) : (
                <div className="space-y-3">
                  <Upload className="w-16 h-16 text-retro-gold/50 mx-auto" />
                  <div className="text-retro-cream font-retro">
                    Drop video file here or click to browse
                  </div>
                  <div className="text-retro-mustard text-xs font-retro">
                    Supports MP4, MOV, AVI, and more
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* AI Input */}
          <div className="card-retro">
            <h3 className="label-retro mb-4">
              <Sparkles className="inline w-5 h-5 mr-2" />
              AI METADATA INPUT
            </h3>

            <div className="space-y-4">
              <div>
                <label className="label-meter block mb-2">TITLE SUMMARY (1-2 sentences) *</label>
                <textarea
                  className="input-retro min-h-[80px]"
                  value={titleInput}
                  onChange={(e) => setTitleInput(e.target.value)}
                  placeholder="e.g., Instrumental version of 'Song Title' by Artist Name"
                  disabled={isGenerating || isUploading}
                />
              </div>

              <div>
                <label className="label-meter block mb-2">ADDITIONAL CONTEXT (Optional)</label>
                <textarea
                  className="input-retro min-h-[80px]"
                  value={descriptionInput}
                  onChange={(e) => setDescriptionInput(e.target.value)}
                  placeholder="Add any extra details for the AI to include..."
                  disabled={isGenerating || isUploading}
                />
              </div>

              {/* Description Style */}
              <div>
                <label className="label-meter block mb-2">
                  <FileText className="inline w-3 h-3 mr-1" />
                  DESCRIPTION STYLE
                </label>
                <div className="flex gap-2">
                  {['minimal', 'balanced', 'detailed'].map((style) => (
                    <button
                      key={style}
                      onClick={() => setDescriptionStyle(style)}
                      className={`
                        flex-1 px-4 py-2 rounded-retro font-retro text-xs uppercase transition-all
                        ${descriptionStyle === style
                          ? 'bg-retro-orange text-white border-2 border-retro-dark-brown shadow-retro'
                          : 'bg-[#3d2817]/30 text-retro-mustard border-2 border-retro-gold/20 hover:bg-[#3d2817]/50'
                        }
                      `}
                      disabled={isGenerating || isUploading}
                    >
                      {style}
                    </button>
                  ))}
                </div>
              </div>

              {/* Tag Count Slider */}
              <div>
                <label className="label-meter block mb-2">
                  <Hash className="inline w-3 h-3 mr-1" />
                  TAG COUNT: {tagCount}
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={tagCount}
                  onChange={(e) => setTagCount(parseInt(e.target.value))}
                  className="w-full h-2 bg-[#2d1f1a] rounded-full appearance-none cursor-pointer
                    [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-6
                    [&::-webkit-slider-thumb]:h-6 [&::-webkit-slider-thumb]:rounded-full
                    [&::-webkit-slider-thumb]:bg-retro-gold [&::-webkit-slider-thumb]:cursor-pointer
                    [&::-webkit-slider-thumb]:shadow-retro-sm"
                  disabled={isGenerating || isUploading}
                />
              </div>

              {/* Generate Button */}
              <button
                onClick={generateMetadata}
                disabled={isGenerating || isUploading || !titleInput.trim()}
                className="btn-retro btn-secondary w-full flex items-center justify-center gap-2"
              >
                <Sparkles className="w-5 h-5" />
                {isGenerating ? 'GENERATING...' : 'GENERATE METADATA'}
              </button>
            </div>
          </div>
        </motion.div>

        {/* Right Column - Preview & Upload */}
        <motion.div
          className="space-y-6"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
        >
          {/* Metadata Preview */}
          <AnimatePresence>
            {generatedTitle && (
              <motion.div
                className="card-retro"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <div className="flex items-center gap-2 mb-4">
                  <Eye className="w-5 h-5 text-retro-gold" />
                  <h3 className="label-retro mb-0">METADATA PREVIEW</h3>
                </div>

                <div className="space-y-4">
                  {/* Title */}
                  <div>
                    <label className="label-meter block mb-2">TITLE</label>
                    <input
                      type="text"
                      className="input-retro"
                      value={generatedTitle}
                      onChange={(e) => setGeneratedTitle(e.target.value)}
                      disabled={isUploading}
                    />
                  </div>

                  {/* Description */}
                  <div>
                    <label className="label-meter block mb-2">DESCRIPTION</label>
                    <textarea
                      className="input-retro min-h-[120px]"
                      value={generatedDescription}
                      onChange={(e) => setGeneratedDescription(e.target.value)}
                      disabled={isUploading}
                    />
                  </div>

                  {/* Tags */}
                  <div>
                    <label className="label-meter block mb-2">TAGS ({generatedTags.length})</label>
                    <div className="flex flex-wrap gap-2">
                      {generatedTags.map((tag, index) => (
                        <span
                          key={index}
                          className="badge-retro bg-retro-teal text-white text-xs"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Upload Settings */}
          <div className="card-retro">
            <h3 className="label-retro mb-4">UPLOAD SETTINGS</h3>

            <div className="space-y-4">
              <div>
                <label className="label-meter block mb-2">PRIVACY STATUS</label>
                <select
                  className="input-retro"
                  value={privacyStatus}
                  onChange={(e) => setPrivacyStatus(e.target.value)}
                  disabled={isUploading}
                >
                  <option value="public">Public</option>
                  <option value="unlisted">Unlisted</option>
                  <option value="private">Private</option>
                </select>
              </div>
            </div>
          </div>

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={isUploading || !videoFile || !generatedTitle}
            className="btn-retro btn-primary w-full flex items-center justify-center gap-3 text-xl py-4"
          >
            <Send className="w-6 h-6" />
            {isUploading ? 'UPLOADING...' : 'UPLOAD TO YOUTUBE'}
          </button>

          {/* Upload Progress */}
          <AnimatePresence>
            {isUploading && (
              <motion.div
                className="card-retro"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
              >
                <h3 className="label-retro mb-4">UPLOAD PROGRESS</h3>

                <div className="progress-retro mb-4">
                  <div
                    className="progress-retro-fill"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>

                <div className="flex justify-between text-retro-cream font-retro text-sm">
                  <span>PROGRESS:</span>
                  <span className="text-retro-gold">{uploadProgress}%</span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Upload Result */}
          <AnimatePresence>
            {uploadResult && (
              <motion.div
                className="card-retro"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <h3 className="label-retro mb-4">UPLOAD COMPLETE!</h3>

                <div className="space-y-3">
                  <div className="p-4 bg-retro-sage/20 rounded-retro border-2 border-retro-sage">
                    <div className="text-retro-cream font-retro font-bold mb-2">
                      Video ID: {uploadResult.video_id}
                    </div>
                    {uploadResult.url && (
                      <a
                        href={uploadResult.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-retro-orange hover:text-retro-gold font-retro underline"
                      >
                        View on YouTube →
                      </a>
                    )}
                  </div>

                  <button
                    onClick={resetForm}
                    className="btn-retro btn-success w-full"
                  >
                    Upload Another Video
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </div>
  )
}
