# steamling.awk - the boot logo as SVG: logo.svg (the still pose the watermark shows) and the
# throbber frames particles-NNNN.svg. A baby dragon peeks over the top edge of the handheld, paws
# on its rim and puffing steam, while the handheld turns over and back. two-step loops the frames
# over a fixed 2 s; the last frame is the still pose, so the loop closes on the watermark.
#   awk -v frames=N -v out=DIR -f steamling.awk
#
# Every frame is the whole picture on black, laid exactly over the watermark (same box and
# mapping), so nothing of the still pose shows through while the handheld is narrow. The dragon
# is drawn in its own artboard units and placed by DRAGON; the handheld keeps the logo-space
# geometry of the Steamling mark, lowered by DROP so the pair sits centred in the box.
BEGIN {
    pi = atan2(0, -1)
    hx = 512.5                  # the handheld's vertical centre line, the axis it turns on
    DROP = 74                   # handheld centre at y 587
    # artboard (480,320) is the handheld centre; 1/0.85 keeps the handheld at its logo size
    DRAGON = "translate(512.5 587) scale(1.17647) translate(-480 -320)"
    AXIS = 480                  # hx in artboard units
    RED = "#D7262E"; DARKRED = "#8A1520"; GOLD = "#D4A64A"; EYE = "#E9C766"
    SILVER = "#C3C7CD"; DARKSILVER = "#7E848C"
    F = frames / 5              # frames per turn over (0.4 s at 60 frames)
    for (f = 0; f < frames; f++) {
        # Hold, turn over, hold, turn back, each turn ending on its half's last frame. The width
        # follows the cosine of the turn, and the left column swaps edge-on (D-pad and stick trade
        # rows: the standard and TOP-DPAD layouts), where the handheld has no width.
        stick_top = (f >= frames / 2)
        sx = 1
        p = f - (frames / 2 - F)
        if (p < 0 || p >= F) p = f - (frames - F)
        if (p >= 0 && p < F) {
            sx = cos(pi * (p + 1) / F); if (sx < 0) sx = -sx
            if (sx < 0.02) sx = 0.02   # edge-on: a sliver, as the edge of a turning card
            stick_top = (f < frames / 2) ? ((p + 1) / F >= 0.5) : ((p + 1) / F < 0.5)
        }
        t = (f + 1) / frames; t -= int(t)   # 0 on the last frame: the still pose
        scene(sprintf("%s/particles-%04d.svg", out, f + 1), sx, stick_top, t, 1)
    }
    scene(out "/logo.svg", 1, 0, 0, 0)
}

function scene(file, sx, stick_top, t, opaque,    turn) {
    print "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"776\" height=\"725\" viewBox=\"124 146 776 725\">" > file
    if (opaque)
        print "  <rect x=\"124\" y=\"146\" width=\"776\" height=\"725\" fill=\"#000\"/>" > file
    printf "  <g transform=\"%s\">\n", DRAGON > file
    behind(file, t)
    print "  </g>" > file
    turn = sprintf("translate(%.2f 0) scale(%.4f 1) translate(%.2f %d)", hx, sx, -hx, DROP)
    handheld(turn, stick_top, file)
    printf "  <g transform=\"%s\">\n", DRAGON > file
    paws(file, sx)
    print "  </g>\n</svg>" > file
    close(file)
}

# Body, wings, tail and head: everything the handheld hides or that rises above its top edge.
function behind(file, t,    a) {
    printf "    <ellipse cx=\"480\" cy=\"300\" rx=\"120\" ry=\"70\" fill=\"%s\"/>\n", RED > file
    printf "    <ellipse cx=\"480\" cy=\"318\" rx=\"70\" ry=\"40\" fill=\"%s\"/>\n", GOLD > file
    wing(file, "translate(404 228) scale(-0.62 0.62) rotate(-18)", RED, SILVER)
    wing(file, "translate(500 226) scale(0.5) rotate(-40)", DARKRED, DARKSILVER)
    # the tail flicks a few degrees about its root in the body; the root shows while the
    # handheld is edge-on, so the tail never floats free of the dragon
    a = 5 * sin(2 * pi * t)
    printf "    <g transform=\"rotate(%.2f 600 300)\">\n", a > file
    printf "      <path d=\"M590,300 L640,300 C700,300 720,270 734,246\" fill=\"none\" stroke=\"%s\" stroke-width=\"10\" stroke-linecap=\"round\"/>\n", RED > file
    printf "      <path d=\"M730,252 L742,222 L754,246 Q742,240 730,252 Z\" fill=\"%s\"/>\n", GOLD > file
    print "    </g>" > file
    print "    <g transform=\"translate(0 12)\">" > file
    head(file)
    steam(file, t)
    print "    </g>" > file
}

function wing(file, transform, fill, bone) {
    printf "    <g transform=\"%s\">\n", transform > file
    printf "      <path d=\"M0,0 C6,-44 30,-84 72,-104 Q80,-74 110,-64 Q94,-40 118,-22 Q80,-26 60,-6 Q30,-14 0,0 Z\" fill=\"%s\"/>\n", fill > file
    printf "      <path d=\"M0,0 L30,-58 L72,-104 M30,-58 L110,-64 M30,-58 L118,-22\" fill=\"none\" stroke=\"%s\" stroke-width=\"3\" stroke-linecap=\"round\"/>\n", bone > file
    print "    </g>" > file
}

function head(file) {
    printf "      <path d=\"M440,140 C430,118 412,108 396,110 C410,118 420,130 426,146 Z\" fill=\"%s\"/>\n", SILVER > file
    printf "      <path d=\"M478,132 C476,110 466,96 452,90 C462,104 466,118 464,136 Z\" fill=\"%s\"/>\n", SILVER > file
    printf "      <path d=\"M420,170 L388,156 L404,176 L386,186 L418,190 Z\" fill=\"%s\"/>\n", DARKRED > file
    printf "      <ellipse cx=\"470\" cy=\"180\" rx=\"58\" ry=\"50\" fill=\"%s\"/>\n", RED > file
    printf "      <ellipse cx=\"522\" cy=\"196\" rx=\"34\" ry=\"24\" fill=\"%s\"/>\n", RED > file
    printf "      <path d=\"M486,148 C496,144 508,148 514,156\" fill=\"none\" stroke=\"%s\" stroke-width=\"4\" stroke-linecap=\"round\"/>\n", DARKRED > file
    printf "      <circle cx=\"490\" cy=\"168\" r=\"13\" fill=\"%s\"/>\n", EYE > file
    print "      <ellipse cx=\"492\" cy=\"168\" rx=\"4\" ry=\"9\" fill=\"#120404\"/>" > file
    print "      <circle cx=\"496\" cy=\"162\" r=\"3\" fill=\"#fff\"/>" > file
    print "      <ellipse cx=\"546\" cy=\"188\" rx=\"3.2\" ry=\"2.2\" fill=\"#3A0A0E\"/>" > file
    print "      <path d=\"M500,210 Q526,220 552,203\" fill=\"none\" stroke=\"#5E0E14\" stroke-width=\"3\" stroke-linecap=\"round\"/>" > file
    print "      <path d=\"M528,214 L532,223 L536,212 Z\" fill=\"#fff\"/>" > file
    printf "      <path d=\"M440,212 C450,206 458,206 466,210\" fill=\"none\" stroke=\"%s\" stroke-width=\"5\" stroke-linecap=\"round\"/>\n", GOLD > file
}

# Four puffs rising from the nostril a quarter of a loop apart: each swells and fades along one
# curve, so the stream looks the same at every frame boundary of the loop.
function steam(file, t,    k, u, x, y, r, o) {
    for (k = 0; k < 4; k++) {
        u = t + k / 4; u -= int(u)
        x = bez(u, 552, 568, 592, 624)
        y = bez(u, 186, 156, 124, 88)
        r = 5 + 17 * u
        o = (u < 0.1 ? u / 0.1 : 1) * (1 - u) ^ 0.9
        if (o < 0.01) continue
        printf "      <g fill=\"#fff\" fill-opacity=\"%.3f\">\n", o > file
        printf "        <circle cx=\"%.2f\" cy=\"%.2f\" r=\"%.2f\"/>\n", x, y, r > file
        printf "        <circle cx=\"%.2f\" cy=\"%.2f\" r=\"%.2f\"/>\n", x + 0.75 * r, y + 0.3 * r, 0.65 * r > file
        printf "        <circle cx=\"%.2f\" cy=\"%.2f\" r=\"%.2f\"/>\n", x - 0.55 * r, y + 0.45 * r, 0.5 * r > file
        print "      </g>" > file
    }
}

function bez(u, a, b, c, d,    v) {
    v = 1 - u
    return v * v * v * a + 3 * v * v * u * b + 3 * v * u * u * c + u * u * u * d
}

# The Steamling mark's handheld under <transform>, its body filled black so it hides the dragon
# behind it. Each side's controls share a column centred between the body's edge and the screen;
# the D-pad and the left stick trade rows when stick_top is set, and the face buttons and the
# right stick never move.
function handheld(transform, stick_top, file,    dx, dy, sx, sy) {
    dx = 346; dy = 475; sx = 346; sy = 557.5
    if (stick_top) { dy = 557.5; sy = 475 }
    printf "  <g transform=\"%s\">\n", transform > file
    print "    <rect x=\"286.5\" y=\"410.5\" width=\"452\" height=\"205\" rx=\"78.5\" fill=\"#000\" stroke=\"#fff\" stroke-width=\"7\"/>" > file
    print "    <rect x=\"404.5\" y=\"449.5\" width=\"217\" height=\"127\" rx=\"10.5\" fill=\"#fff\" fill-opacity=\"0.05\" stroke=\"#fff\" stroke-width=\"5\"/>" > file
    printf "    <rect x=\"%.1f\" y=\"%.1f\" width=\"46\" height=\"14\" rx=\"2.5\" fill=\"#fff\"/>\n", dx - 23, dy - 7 > file
    printf "    <rect x=\"%.1f\" y=\"%.1f\" width=\"14\" height=\"46\" rx=\"2.5\" fill=\"#fff\"/>\n", dx - 7, dy - 23 > file
    print "    <circle cx=\"679\" cy=\"456.5\" r=\"7\" fill=\"#fff\"/>" > file
    print "    <circle cx=\"660.9\" cy=\"474.7\" r=\"7\" fill=\"#fff\"/>" > file
    print "    <circle cx=\"697.1\" cy=\"474.6\" r=\"7\" fill=\"#fff\"/>" > file
    print "    <circle cx=\"679.1\" cy=\"492.7\" r=\"7\" fill=\"#fff\"/>" > file
    printf "    <circle cx=\"%.1f\" cy=\"%.1f\" r=\"18.7\" fill=\"none\" stroke=\"#fff\" stroke-width=\"5\"/>\n", sx, sy > file
    print "    <circle cx=\"679\" cy=\"557.5\" r=\"18.7\" fill=\"none\" stroke=\"#fff\" stroke-width=\"5\"/>" > file
    printf "    <circle cx=\"%.1f\" cy=\"%.1f\" r=\"5\" fill=\"#fff\"/>\n", sx, sy > file
    print "    <circle cx=\"679\" cy=\"557.5\" r=\"5\" fill=\"#fff\"/>" > file
    print "  </g>" > file
}

# The front paws hook over the rim and ride its turning edge inward; they keep their own shape.
function paws(file, sx,    i, px, c) {
    for (i = 0; i < 2; i++) {
        px = AXIS + ((i ? 540 : 420) - AXIS) * sx
        printf "    <ellipse cx=\"%.2f\" cy=\"236\" rx=\"22\" ry=\"11\" fill=\"%s\"/>\n", px, RED > file
        printf "    <path d=\"M%.2f,243 l-2,10 M%.2f,246 l-1,11 M%.2f,244 l1,10\" fill=\"none\" stroke=\"%s\" stroke-width=\"3.5\" stroke-linecap=\"round\"/>\n", \
            px - 14, px - 2, px + 10, SILVER > file
    }
}
