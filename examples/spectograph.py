
import chaudio
import chaudio.visuals

#y = chaudio.waves.square(chaudio.times(5), 320)
y = chaudio.fromfile("arranged.wav")


spec = chaudio.visuals.Spectograph(y)

spec.show()
#spec.save("spec.mp4")

#Writer = animation.writers['ffmpeg']
#writer = Writer(fps=24, metadata=dict(artist='Me'), bitrate=1800)

#ani.save('lines.gif', writer='imagemagick', fps=60)

#ani.save('lines.mp4', writer='ffmpeg', fps=60)


#plt.show()