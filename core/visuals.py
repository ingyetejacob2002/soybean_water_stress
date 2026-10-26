"""Generated illustrations for SoyStress AI (no downloads needed).
Drop your own photos in an `assets/` folder (hero.jpg, class_0.jpg ... class_5.jpg)
and they automatically replace the generated artwork."""
import base64, os

RAMP = ["#2f8f4e", "#6fae48", "#b9bf3a", "#e2a62e", "#c76a2a", "#85502a"]


def _uri(svg):
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def _asset(name):
    base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
    for ext, mime in (("jpg", "jpeg"), ("jpeg", "jpeg"), ("png", "png"), ("webp", "webp")):
        p = os.path.join(base, f"{name}.{ext}")
        if os.path.exists(p):
            with open(p, "rb") as fh:
                return f"data:image/{mime};base64," + base64.b64encode(fh.read()).decode()
    return None


def _mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def leaf_uri(s):
    """Soybean trifoliate leaf for wilting class s (0-5): colour fades, leaflets droop and curl."""
    u = _asset(f"class_{s}")
    if u:
        return u
    t = s / 5
    c = RAMP[s]
    dk, lt = _mix(c, "#000000", .28), _mix(c, "#ffffff", .45)

    def leaflet(a):
        rx, ry = 54, 31 - 11 * t
        scorch = (f'<ellipse cx="{rx}" rx="{rx - 2}" ry="{ry - 1}" fill="none" stroke="#6b3f1d" '
                  f'stroke-width="{2 + 5 * t:.1f}" stroke-opacity="{min(1, max(0, t - .4) * 1.2):.2f}" '
                  f'stroke-dasharray="9 7"/>')
        return (f'<g transform="translate(120 112) rotate({a:.1f})">'
                f'<ellipse cx="{rx}" rx="{rx}" ry="{ry:.1f}" fill="{c}" stroke="{dk}" stroke-width="2"/>'
                f'<path d="M0 0H{2 * rx}" stroke="{lt}" stroke-width="2"/>{scorch}</g>')

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 210">'
        '<defs><linearGradient id="b" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#f4f9f5"/><stop offset="1" stop-color="#dcebdf"/></linearGradient></defs>'
        '<rect width="240" height="210" rx="18" fill="url(#b)"/>'
        '<ellipse cx="120" cy="200" rx="86" ry="14" fill="#8a6a45" opacity=".35"/>'
        f'<path d="M120 198 Q{120 + 32 * t:.0f} 158 120 112" stroke="#3f6b3a" stroke-width="5" '
        'fill="none" stroke-linecap="round"/>'
        + leaflet(205 - 60 * t) + leaflet(-25 + 60 * t) + leaflet(-90 + 45 * t) + '</svg>')
    return _uri(svg)


def hero_uri():
    """Soybean-field banner."""
    u = _asset("hero")
    if u:
        return u
    p = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 420" preserveAspectRatio="xMidYMid slice">'
         '<defs><linearGradient id="s" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b2116"/>'
         '<stop offset=".6" stop-color="#1d5130"/><stop offset="1" stop-color="#3b8a58"/></linearGradient>'
         '<radialGradient id="g"><stop offset="0" stop-color="#e3f7b8" stop-opacity=".9"/>'
         '<stop offset="1" stop-color="#e3f7b8" stop-opacity="0"/></radialGradient></defs>'
         '<rect width="1200" height="420" fill="url(#s)"/><circle cx="960" cy="120" r="170" fill="url(#g)"/>'
         '<path d="M0 250Q300 180 600 245T1200 215V420H0Z" fill="#14391f" opacity=".75"/>'
         '<path d="M0 300Q350 240 700 295T1200 270V420H0Z" fill="#10301a" opacity=".9"/>']
    for r in range(7):
        y, k = 290 + r * 20, .5 + r * .17
        fill = _mix("#2c7448", "#8fd16a", r / 7)
        step = max(34, int(78 * k))
        for x in range(-20 + (r % 2) * step // 2, 1240, step):
            p.append(f'<g transform="translate({x} {y}) scale({k:.2f})" fill="{fill}">'
                     '<ellipse cx="-15" cy="-12" rx="15" ry="7" transform="rotate(-25 -15 -12)"/>'
                     '<ellipse cx="15" cy="-12" rx="15" ry="7" transform="rotate(25 15 -12)"/>'
                     '<ellipse cx="0" cy="-22" rx="7" ry="15"/></g>')
    p.append('</svg>')
    return _uri("".join(p))
