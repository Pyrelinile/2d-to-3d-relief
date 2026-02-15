from PIL import Image

from twod_to_threed_relief.core.imageproc import build_heightmap, map_height_range


def test_heightmap_shape_and_range() -> None:
    img = Image.new("RGB", (32, 16), "white")
    hm = build_heightmap(img, mesh_x=20, mesh_y=10)
    assert hm.shape == (10, 20)
    th = map_height_range(hm, 0.8, 3.2)
    assert float(th.min()) >= 0.8
    assert float(th.max()) <= 3.2
