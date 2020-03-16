from zheye import zheye
z = zheye()
positions = z.Recognize('realcap/a.gif')
if positions[0][1] > positions[1][1]:
    positions = [positions[1], positions[0]]

positions = [(p[1], p[0]) for p in positions]

print(positions)
