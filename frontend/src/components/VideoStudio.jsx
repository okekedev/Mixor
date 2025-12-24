import { Video } from 'lucide-react'

export default function VideoStudio() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card-retro">
        <div className="flex items-center gap-3 mb-2">
          <Video className="w-8 h-8 text-retro-gold" />
          <div>
            <h2 className="font-display text-3xl text-retro-gold">VIDEO STUDIO</h2>
            <p className="text-retro-mustard font-retro text-sm">Advanced video creation and mixing controls</p>
          </div>
        </div>
      </div>

      {/* Coming Soon Message */}
      <div className="card-retro">
        <div className="glass-retro p-12 text-center">
          <Video className="w-24 h-24 text-retro-gold/50 mx-auto mb-6" />
          <h3 className="font-display text-2xl text-retro-gold mb-3">ADVANCED CONTROLS</h3>
          <p className="text-retro-cream font-retro text-lg mb-6">
            Coming Soon - Professional video mixing and mastering tools
          </p>
          <div className="space-y-2 text-retro-mustard font-retro text-sm max-w-md mx-auto">
            <p>• Custom background video selection</p>
            <p>• EQ visualizer customization</p>
            <p>• Advanced audio/video sync controls</p>
            <p>• Color grading and effects</p>
            <p>• Batch processing with custom settings</p>
          </div>
        </div>
      </div>

      {/* Placeholder for future features */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card-retro">
          <h3 className="label-retro mb-4">BACKGROUND MIXER</h3>
          <div className="glass-retro p-6 text-center">
            <p className="text-retro-mustard font-retro text-sm">
              Mix custom background videos from your library
            </p>
          </div>
        </div>

        <div className="card-retro">
          <h3 className="label-retro mb-4">VISUALIZER CONTROLS</h3>
          <div className="glass-retro p-6 text-center">
            <p className="text-retro-mustard font-retro text-sm">
              Customize EQ spectrum colors and animations
            </p>
          </div>
        </div>

        <div className="card-retro">
          <h3 className="label-retro mb-4">AUDIO MASTERING</h3>
          <div className="glass-retro p-6 text-center">
            <p className="text-retro-mustard font-retro text-sm">
              Fine-tune loudness, EQ, and compression
            </p>
          </div>
        </div>

        <div className="card-retro">
          <h3 className="label-retro mb-4">BATCH PROCESSING</h3>
          <div className="glass-retro p-6 text-center">
            <p className="text-retro-mustard font-retro text-sm">
              Process multiple videos with custom presets
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
