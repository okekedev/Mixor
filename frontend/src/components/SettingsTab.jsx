import { useState } from 'react'
import { Save, Key, Globe, Settings as SettingsIcon } from 'lucide-react'
import { motion } from 'framer-motion'

export default function SettingsTab() {
  const [settings, setSettings] = useState({
    youtubeClientId: '',
    youtubeClientSecret: '',
    youtubeRefreshToken: '',
    ollamaUrl: 'http://localhost:11434',
    ollamaModel: 'llama3.2:3b',
    defaultCity: 'atlanta',
    targetLufs: '-14.0',
  })

  const [saved, setSaved] = useState(false)

  const handleSave = async () => {
    // TODO: Implement save to backend
    console.log('Saving settings:', settings)
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  const handleChange = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }))
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card-retro">
        <div className="flex items-center gap-3 mb-4">
          <SettingsIcon className="w-8 h-8 text-retro-gold" />
          <div>
            <h2 className="font-display text-3xl text-retro-gold">STUDIO CONFIGURATION</h2>
            <p className="text-retro-mustard font-retro text-sm">Configure your Mixor environment</p>
          </div>
        </div>
      </div>

      {/* YouTube API Settings */}
      <motion.div
        className="card-retro"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className="flex items-center gap-2 mb-6">
          <Key className="w-6 h-6 text-retro-orange" />
          <h3 className="label-retro">YouTube API Credentials</h3>
        </div>

        <div className="space-y-4">
          <div>
            <label className="label-meter block mb-2">CLIENT ID</label>
            <input
              type="text"
              className="input-retro"
              value={settings.youtubeClientId}
              onChange={(e) => handleChange('youtubeClientId', e.target.value)}
              placeholder="Enter YouTube Client ID"
            />
          </div>

          <div>
            <label className="label-meter block mb-2">CLIENT SECRET</label>
            <input
              type="password"
              className="input-retro"
              value={settings.youtubeClientSecret}
              onChange={(e) => handleChange('youtubeClientSecret', e.target.value)}
              placeholder="Enter YouTube Client Secret"
            />
          </div>

          <div>
            <label className="label-meter block mb-2">REFRESH TOKEN</label>
            <input
              type="password"
              className="input-retro"
              value={settings.youtubeRefreshToken}
              onChange={(e) => handleChange('youtubeRefreshToken', e.target.value)}
              placeholder="Enter YouTube Refresh Token"
            />
          </div>
        </div>
      </motion.div>

      {/* Ollama Settings */}
      <motion.div
        className="card-retro"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <div className="flex items-center gap-2 mb-6">
          <Globe className="w-6 h-6 text-retro-teal" />
          <h3 className="label-retro">AI Configuration</h3>
        </div>

        <div className="space-y-4">
          <div>
            <label className="label-meter block mb-2">OLLAMA URL</label>
            <input
              type="text"
              className="input-retro"
              value={settings.ollamaUrl}
              onChange={(e) => handleChange('ollamaUrl', e.target.value)}
              placeholder="http://localhost:11434"
            />
          </div>

          <div>
            <label className="label-meter block mb-2">OLLAMA MODEL</label>
            <input
              type="text"
              className="input-retro"
              value={settings.ollamaModel}
              onChange={(e) => handleChange('ollamaModel', e.target.value)}
              placeholder="llama3.2:3b"
            />
          </div>
        </div>
      </motion.div>

      {/* Audio Settings */}
      <motion.div
        className="card-retro"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <h3 className="label-retro mb-6">AUDIO PROCESSING</h3>

        <div className="space-y-4">
          <div>
            <label className="label-meter block mb-2">TARGET LOUDNESS (LUFS)</label>
            <input
              type="text"
              className="input-retro"
              value={settings.targetLufs}
              onChange={(e) => handleChange('targetLufs', e.target.value)}
              placeholder="-14.0"
            />
            <p className="text-retro-mustard/70 text-xs mt-2 font-retro">
              Streaming platform standard: -14.0 LUFS
            </p>
          </div>

          <div>
            <label className="label-meter block mb-2">DEFAULT CITY FOR BACKGROUNDS</label>
            <input
              type="text"
              className="input-retro"
              value={settings.defaultCity}
              onChange={(e) => handleChange('defaultCity', e.target.value)}
              placeholder="atlanta"
            />
          </div>
        </div>
      </motion.div>

      {/* Save Button */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
      >
        <button
          onClick={handleSave}
          className="btn-retro btn-primary w-full flex items-center justify-center gap-3"
        >
          <Save className="w-5 h-5" />
          {saved ? 'SETTINGS SAVED!' : 'SAVE CONFIGURATION'}
        </button>
      </motion.div>
    </div>
  )
}
