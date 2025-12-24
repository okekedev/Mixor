import { useState, useEffect } from 'react'
import { ListMusic, Plus, Trash2, Eye, TrendingUp, RefreshCw } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { api } from '../lib/api'

export default function PlaylistManager() {
  const [playlists, setPlaylists] = useState([])
  const [selectedPlaylist, setSelectedPlaylist] = useState(null)
  const [playlistVideos, setPlaylistVideos] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  const [newPlaylistName, setNewPlaylistName] = useState('')
  const [newPlaylistDesc, setNewPlaylistDesc] = useState('')

  useEffect(() => {
    loadPlaylists()
  }, [])

  const loadPlaylists = async () => {
    setIsLoading(true)
    try {
      const data = await api.getPlaylists()
      setPlaylists(data.playlists || [])
    } catch (error) {
      console.error('Error loading playlists:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const loadPlaylistVideos = async (playlistId) => {
    setIsLoading(true)
    try {
      const data = await api.getPlaylistVideos(playlistId)
      setPlaylistVideos(data.videos || [])
      const playlist = playlists.find(p => p.id === playlistId)
      setSelectedPlaylist(playlist)
    } catch (error) {
      console.error('Error loading playlist videos:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const createPlaylist = async () => {
    if (!newPlaylistName.trim()) {
      alert('Please enter a playlist name')
      return
    }

    setIsLoading(true)
    try {
      await api.createPlaylist(newPlaylistName, newPlaylistDesc, 'public')
      setNewPlaylistName('')
      setNewPlaylistDesc('')
      setIsCreating(false)
      await loadPlaylists()
    } catch (error) {
      console.error('Error creating playlist:', error)
      alert('Failed to create playlist: ' + error.message)
    } finally {
      setIsLoading(false)
    }
  }

  const deleteVideo = async (videoId) => {
    if (!confirm('Are you sure you want to delete this video from YouTube?')) return

    try {
      await api.deleteVideo(videoId)
      // Refresh playlist
      if (selectedPlaylist) {
        await loadPlaylistVideos(selectedPlaylist.id)
      }
    } catch (error) {
      console.error('Error deleting video:', error)
      alert('Failed to delete video: ' + error.message)
    }
  }

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
    return num
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card-retro">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <ListMusic className="w-8 h-8 text-retro-gold" />
            <div>
              <h2 className="font-display text-3xl text-retro-gold">PLAYLIST MANAGER</h2>
              <p className="text-retro-mustard font-retro text-sm">Manage your YouTube playlists and videos</p>
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={loadPlaylists}
              className="btn-retro btn-secondary flex items-center gap-2"
              disabled={isLoading}
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
              REFRESH
            </button>

            <button
              onClick={() => setIsCreating(true)}
              className="btn-retro btn-primary flex items-center gap-2"
              disabled={isLoading}
            >
              <Plus className="w-4 h-4" />
              NEW PLAYLIST
            </button>
          </div>
        </div>
      </div>

      {/* Create Playlist Modal */}
      <AnimatePresence>
        {isCreating && (
          <motion.div
            className="card-retro"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <h3 className="label-retro mb-4">CREATE NEW PLAYLIST</h3>

            <div className="space-y-4">
              <div>
                <label className="label-meter block mb-2">PLAYLIST NAME *</label>
                <input
                  type="text"
                  className="input-retro"
                  value={newPlaylistName}
                  onChange={(e) => setNewPlaylistName(e.target.value)}
                  placeholder="Enter playlist name..."
                  disabled={isLoading}
                />
              </div>

              <div>
                <label className="label-meter block mb-2">DESCRIPTION (Optional)</label>
                <textarea
                  className="input-retro min-h-[80px]"
                  value={newPlaylistDesc}
                  onChange={(e) => setNewPlaylistDesc(e.target.value)}
                  placeholder="Enter playlist description..."
                  disabled={isLoading}
                />
              </div>

              <div className="flex gap-2">
                <button
                  onClick={createPlaylist}
                  className="btn-retro btn-primary flex-1"
                  disabled={isLoading || !newPlaylistName.trim()}
                >
                  CREATE
                </button>
                <button
                  onClick={() => {
                    setIsCreating(false)
                    setNewPlaylistName('')
                    setNewPlaylistDesc('')
                  }}
                  className="btn-retro btn-danger flex-1"
                  disabled={isLoading}
                >
                  CANCEL
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Playlists List */}
        <motion.div
          className="lg:col-span-1 space-y-3"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <div className="card-retro">
            <h3 className="label-retro mb-4">YOUR PLAYLISTS ({playlists.length})</h3>

            {isLoading && !playlists.length ? (
              <div className="text-center py-8">
                <div className="spinner-retro mx-auto mb-3"></div>
                <p className="text-retro-mustard font-retro text-sm">Loading playlists...</p>
              </div>
            ) : playlists.length === 0 ? (
              <div className="glass-retro p-6 text-center">
                <ListMusic className="w-12 h-12 text-retro-gold/50 mx-auto mb-3" />
                <p className="text-retro-mustard font-retro text-sm">No playlists found</p>
              </div>
            ) : (
              <div className="space-y-2 max-h-[600px] overflow-y-auto">
                {playlists.map((playlist) => (
                  <button
                    key={playlist.id}
                    onClick={() => loadPlaylistVideos(playlist.id)}
                    className={`
                      w-full text-left p-3 rounded-retro transition-all
                      ${selectedPlaylist?.id === playlist.id
                        ? 'bg-retro-orange text-white shadow-retro'
                        : 'bg-[#3d2817]/30 text-retro-cream hover:bg-[#3d2817]/50'
                      }
                    `}
                  >
                    <div className="font-retro font-bold text-sm truncate">
                      {playlist.title}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </motion.div>

        {/* Playlist Videos */}
        <motion.div
          className="lg:col-span-2 space-y-3"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
        >
          {selectedPlaylist ? (
            <div className="card-retro">
              <div className="flex items-center justify-between mb-4">
                <h3 className="label-retro mb-0">{selectedPlaylist.title}</h3>
                <span className="badge-retro bg-retro-teal">{playlistVideos.length} VIDEOS</span>
              </div>

              {isLoading ? (
                <div className="text-center py-12">
                  <div className="spinner-retro mx-auto mb-3"></div>
                  <p className="text-retro-mustard font-retro text-sm">Loading videos...</p>
                </div>
              ) : playlistVideos.length === 0 ? (
                <div className="glass-retro p-12 text-center">
                  <Eye className="w-16 h-16 text-retro-gold/50 mx-auto mb-3" />
                  <p className="text-retro-mustard font-retro">This playlist is empty</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-[600px] overflow-y-auto">
                  {playlistVideos.map((video) => (
                    <motion.div
                      key={video.id}
                      className="p-4 bg-[#3d2817]/30 rounded-retro border-2 border-retro-gold/20 hover:border-retro-gold/50 transition-all"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                    >
                      <div className="flex items-start gap-4">
                        {/* Thumbnail */}
                        {video.thumbnail && (
                          <img
                            src={video.thumbnail}
                            alt={video.title}
                            className="w-32 h-20 object-cover rounded-retro-sm border-2 border-retro-gold/30"
                          />
                        )}

                        {/* Video Info */}
                        <div className="flex-1 min-w-0">
                          <h4 className="text-retro-cream font-retro font-bold mb-2 truncate">
                            {video.title}
                          </h4>

                          <div className="flex items-center gap-4 text-retro-mustard text-xs font-retro">
                            <div className="flex items-center gap-1">
                              <Eye className="w-3 h-3" />
                              {formatNumber(video.view_count || 0)}
                            </div>
                            <div className="flex items-center gap-1">
                              <TrendingUp className="w-3 h-3" />
                              {formatNumber(video.like_count || 0)}
                            </div>
                          </div>
                        </div>

                        {/* Actions */}
                        <div className="flex flex-col gap-2">
                          <a
                            href={`https://www.youtube.com/watch?v=${video.id}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="btn-retro btn-secondary text-xs px-3 py-1"
                          >
                            VIEW
                          </a>
                          <button
                            onClick={() => deleteVideo(video.id)}
                            className="btn-retro btn-danger text-xs px-3 py-1 flex items-center gap-1"
                          >
                            <Trash2 className="w-3 h-3" />
                            DELETE
                          </button>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="card-retro">
              <div className="glass-retro p-12 text-center">
                <ListMusic className="w-24 h-24 text-retro-gold/50 mx-auto mb-6" />
                <h3 className="font-display text-2xl text-retro-gold mb-3">SELECT A PLAYLIST</h3>
                <p className="text-retro-mustard font-retro">
                  Choose a playlist from the left to view and manage its videos
                </p>
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  )
}
