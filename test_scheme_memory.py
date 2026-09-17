from backend.scene_memory import SceneMemory


scene = SceneMemory()


scene.update(
    1,
    "truck",
    "CENTER",
    "CLOSE",
    "APPROACHING",
    0.91
)

scene.update(
    2,
    "person",
    "LEFT",
    "MEDIUM",
    "STABLE",
    0.87
)

scene.update(
    3,
    "car",
    "RIGHT",
    "FAR",
    "STABLE",
    0.94
)


print(
    scene.describe_scene()
)

print(
    scene.describe_direction(
        "CENTER"
    )
)

print(
    scene.describe_direction(
        "LEFT"
    )
)

print(
    scene.describe_direction(
        "RIGHT"
    )
)

print(
    scene.describe_object(
        "truck"
    )
)

print(
    scene.describe_object(
        "bicycle"
    )
)
