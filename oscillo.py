import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Variables globales pour chaque canal (initialisées à None)
channel = [None, None, None, None]

window_size = 300
ydata = [[0]*window_size for _ in range(4)]  # 4 listes de données
xdata = list(range(-window_size + 1, 1))

plt.style.use('dark_background')

fig, ax = plt.subplots()
colors = ['orange', 'green', 'red', 'blue']
lines = []

for i in range(4):
    line, = ax.plot(xdata, ydata[i], color=colors[i], label=f'Channel {i+1}')
    lines.append(line)

ax.set_ylim(-2, 2)
ax.set_xlim(-window_size, 0)
ax.set_xlabel("Points")
ax.set_ylabel("Amplitude")
ax.set_title("Gestion du CAP")
ax.legend(loc='upper right')

def update(frame):
    global ydata, channel

    for i in range(4):
        if channel[i] is not None:
            ydata[i].append(channel[i])
            ydata[i].pop(0)
            lines[i].set_ydata(ydata[i])
            lines[i].set_visible(True)  # affiche la courbe
        else:
            # Si None, ne mets rien à jour dans ydata pour éviter la propagation
            # Et cache la courbe
            lines[i].set_visible(False)

    return lines

def init(y_min=-1, y_max=1):
    ax.set_ylim(y_min, y_max)
    ani = animation.FuncAnimation(fig, update, interval=30, blit=True)
    plt.show()