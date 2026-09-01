from converter import convert


output = convert(
    "Color Maze Master_2026-08-27_451346.html",
    "dee97dee6e36eb83807c318969cf5ef2834f6a6a_v1_js_load.js"
)


with open(
    "google_ready.html",
    "w",
    encoding="utf-8"
) as f:
    f.write(output)


print("Conversion completed!")
