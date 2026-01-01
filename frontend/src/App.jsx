import { useState, useEffect } from 'react'
import { Music, Settings, Video, Upload, ListMusic, Disc3 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import SettingsTab from './components/SettingsTab'
import InstrumentalMaker from './components/InstrumentalMaker'
import VideoStudio from './components/VideoStudio'
import YouTubeUploader from './components/YouTubeUploader'
import PlaylistManager from './components/PlaylistManager'

function App() {
  const [activeTab, setActiveTab] = useState('instrumental')
  const [vuLevel, setVuLevel] = useState(0)

  const tabs = [
    { id: 'instrumental', label: 'Separate Vocals', icon: Music },
    { id: 'studio', label: 'Video Studio', icon: Video },
    { id: 'upload', label: 'YouTube Uploader', icon: Upload },
    { id: 'playlists', label: 'Playlist Manager', icon: ListMusic },
    { id: 'settings', label: 'Settings', icon: Settings },
  ]

  // Animate VU meter randomly like a real studio meter
  useEffect(() => {
    const interval = setInterval(() => {
      // Random level between 20-95% with some smoothing
      const newLevel = 20 + Math.random() * 75
      setVuLevel(newLevel)
    }, 150)

    return () => clearInterval(interval)
  }, [])

  const renderTab = () => {
    switch (activeTab) {
      case 'instrumental':
        return <InstrumentalMaker />
      case 'studio':
        return <VideoStudio />
      case 'upload':
        return <YouTubeUploader />
      case 'playlists':
        return <PlaylistManager />
      case 'settings':
        return <SettingsTab />
      default:
        return <InstrumentalMaker />
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Studio Header */}
      <header className="header-retro">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            {/* Logo/Branding */}
            <motion.div
              className="flex items-center gap-4"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
            >
              <motion.div
                className="relative"
                animate={{ rotate: 360 }}
                transition={{
                  duration: 8,
                  repeat: Infinity,
                  ease: "linear"
                }}
              >
                <Disc3 className="w-12 h-12 text-retro-gold" />
                <div className="absolute inset-0 bg-retro-orange/20 rounded-full blur-xl"></div>
              </motion.div>
              <div>
                <h1 className="text-4xl font-display text-retro-gold tracking-wider [text-shadow:2px_2px_4px_rgba(0,0,0,0.8)]">
                  MIXOR
                </h1>
              </div>
            </motion.div>

            {/* VU Meter - Classic Studio Style */}
            <motion.div
              className="flex flex-col gap-2"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
            >
              <div className="flex items-center gap-3">
                <span className="label-meter">SIGNAL</span>
                <div className="relative w-64 h-8 bg-[#1a1410] border-3 border-retro-gold rounded-retro overflow-hidden shadow-[inset_0_2px_8px_rgba(0,0,0,0.8)]">
                  {/* VU Meter Background Segments */}
                  <div className="absolute inset-0 flex">
                    {/* Green zone: 0-70% */}
                    <div className="flex-[7] bg-gradient-to-r from-[#2d5016] to-[#3d6820] border-r border-black/50"></div>
                    {/* Yellow zone: 70-85% */}
                    <div className="flex-[15] bg-gradient-to-r from-[#5d4a10] to-[#6d5a15] border-r border-black/50"></div>
                    {/* Red zone: 85-100% */}
                    <div className="flex-[15] bg-gradient-to-r from-[#6d1a1a] to-[#8d2020]"></div>
                  </div>

                  {/* Animated Level Indicator */}
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-[#4CAF50] via-[#FFEB3B] to-[#F44336] opacity-80 shadow-[0_0_10px_currentColor]"
                    style={{
                      width: `${vuLevel}%`,
                      transition: 'width 0.1s ease-out'
                    }}
                  />

                  {/* Scale Marks */}
                  <div className="absolute inset-0 flex justify-between items-center px-1 pointer-events-none">
                    {[...Array(10)].map((_, i) => (
                      <div key={i} className="w-[1px] h-full bg-black/30"></div>
                    ))}
                  </div>
                </div>
                <span className="label-meter text-retro-sage">ACTIVE</span>
              </div>
            </motion.div>
          </div>
        </div>
      </header>

      {/* Tab Navigation - Studio Console Style */}
      <nav className="panel-wood border-b-0">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center gap-2 overflow-x-auto">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`tab-retro flex items-center gap-2 whitespace-nowrap ${
                    activeTab === tab.id ? 'tab-retro-active' : ''
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span>{tab.label}</span>
                </button>
              )
            })}
          </div>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl mx-auto px-6 py-8 w-full flex flex-col">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            {renderTab()}
          </motion.div>
        </AnimatePresence>
      </main>

      {/* Footer - Studio Info */}
      <footer className="border-t-4 border-retro-gold/30 mt-12">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between text-retro-mustard/70 text-sm font-retro">
            <p>© 2025 MIXOR STUDIO • VINTAGE CONTENT WORKSHOP</p>
            <p>EST. 1965 • REMIXED 2025</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
