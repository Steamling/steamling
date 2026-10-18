# steamling.awk - the boot logo as SVG: logo.svg (the still pose the watermark shows) and the
# throbber frames particles-NNNN.svg. A baby dragon peeks over the top edge of the handheld, paws
# on its rim and puffing steam, while the handheld turns over and back. two-step loops the frames
# over a fixed 2 s; the last frame is the still pose, so the loop closes on the watermark.
#   awk -v frames=N -v out=DIR -f steamling.awk
#
# Every part carries the logo's polish: a dark ink line and a soft toon shade from the ink*
# filters (the same filters and units as steamling-logo.svg), a contact shadow under the paws and
# a bevelled handheld with a screen glare. librsvg renders all of it at build time, so the boot
# itself only shows PNGs.
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
    SILVER = "#C3C7CD"; DARKSILVER = "#7E848C"; CLAW = "#D9DCE1"
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
    defs(file)
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

function defs(file) {
    print "  <defs>" > file
    print "  <filter id=\"inkRed\" x=\"-25%\" y=\"-25%\" width=\"150%\" height=\"150%\" color-interpolation-filters=\"sRGB\">" > file
    print "    <feMorphology in=\"SourceAlpha\" operator=\"dilate\" radius=\"2.4\" result=\"grow\"/>" > file
    print "    <feGaussianBlur in=\"grow\" stdDeviation=\"0.3\" result=\"growsoft\"/>" > file
    print "    <feFlood flood-color=\"#2A0508\"/>" > file
    print "    <feComposite in2=\"growsoft\" operator=\"in\" result=\"line\"/>" > file
    print "    <feOffset in=\"SourceAlpha\" dx=\"-5.0\" dy=\"-7.0\" result=\"up\"/>" > file
    print "    <feComposite in=\"SourceAlpha\" in2=\"up\" operator=\"out\" result=\"low\"/>" > file
    print "    <feGaussianBlur in=\"low\" stdDeviation=\"3.15\"/>" > file
    print "    <feComposite in2=\"SourceAlpha\" operator=\"in\" result=\"lowin\"/>" > file
    print "    <feFlood flood-color=\"#4A0A10\" flood-opacity=\"0.6\"/>" > file
    print "    <feComposite in2=\"lowin\" operator=\"in\" result=\"shadow\"/>" > file
    print "    <feOffset in=\"SourceAlpha\" dx=\"4.0\" dy=\"5.0\" result=\"dn\"/>" > file
    print "    <feComposite in=\"SourceAlpha\" in2=\"dn\" operator=\"out\" result=\"high\"/>" > file
    print "    <feGaussianBlur in=\"high\" stdDeviation=\"2.00\"/>" > file
    print "    <feComposite in2=\"SourceAlpha\" operator=\"in\" result=\"highin\"/>" > file
    print "    <feFlood flood-color=\"#FF9C8F\" flood-opacity=\"0.5\"/>" > file
    print "    <feComposite in2=\"highin\" operator=\"in\" result=\"light\"/>" > file
    print "    <feMerge><feMergeNode in=\"line\"/><feMergeNode in=\"SourceGraphic\"/><feMergeNode in=\"shadow\"/><feMergeNode in=\"light\"/></feMerge>" > file
    print "  </filter>" > file
    print "  <filter id=\"inkDark\" x=\"-25%\" y=\"-25%\" width=\"150%\" height=\"150%\" color-interpolation-filters=\"sRGB\">" > file
    print "    <feMorphology in=\"SourceAlpha\" operator=\"dilate\" radius=\"2.4\" result=\"grow\"/>" > file
    print "    <feGaussianBlur in=\"grow\" stdDeviation=\"0.3\" result=\"growsoft\"/>" > file
    print "    <feFlood flood-color=\"#1E0305\"/>" > file
    print "    <feComposite in2=\"growsoft\" operator=\"in\" result=\"line\"/>" > file
    print "    <feOffset in=\"SourceAlpha\" dx=\"-4.0\" dy=\"-6.0\" result=\"up\"/>" > file
    print "    <feComposite in=\"SourceAlpha\" in2=\"up\" operator=\"out\" result=\"low\"/>" > file
    print "    <feGaussianBlur in=\"low\" stdDeviation=\"2.70\"/>" > file
    print "    <feComposite in2=\"SourceAlpha\" operator=\"in\" result=\"lowin\"/>" > file
    print "    <feFlood flood-color=\"#2A0508\" flood-opacity=\"0.55\"/>" > file
    print "    <feComposite in2=\"lowin\" operator=\"in\" result=\"shadow\"/>" > file
    print "    <feOffset in=\"SourceAlpha\" dx=\"3.0\" dy=\"4.0\" result=\"dn\"/>" > file
    print "    <feComposite in=\"SourceAlpha\" in2=\"dn\" operator=\"out\" result=\"high\"/>" > file
    print "    <feGaussianBlur in=\"high\" stdDeviation=\"1.60\"/>" > file
    print "    <feComposite in2=\"SourceAlpha\" operator=\"in\" result=\"highin\"/>" > file
    print "    <feFlood flood-color=\"#E0545B\" flood-opacity=\"0.45\"/>" > file
    print "    <feComposite in2=\"highin\" operator=\"in\" result=\"light\"/>" > file
    print "    <feMerge><feMergeNode in=\"line\"/><feMergeNode in=\"SourceGraphic\"/><feMergeNode in=\"shadow\"/><feMergeNode in=\"light\"/></feMerge>" > file
    print "  </filter>" > file
    print "  <filter id=\"inkSilver\" x=\"-25%\" y=\"-25%\" width=\"150%\" height=\"150%\" color-interpolation-filters=\"sRGB\">" > file
    print "    <feMorphology in=\"SourceAlpha\" operator=\"dilate\" radius=\"1.8\" result=\"grow\"/>" > file
    print "    <feGaussianBlur in=\"grow\" stdDeviation=\"0.3\" result=\"growsoft\"/>" > file
    print "    <feFlood flood-color=\"#1C1D21\"/>" > file
    print "    <feComposite in2=\"growsoft\" operator=\"in\" result=\"line\"/>" > file
    print "    <feOffset in=\"SourceAlpha\" dx=\"-3.0\" dy=\"-4.0\" result=\"up\"/>" > file
    print "    <feComposite in=\"SourceAlpha\" in2=\"up\" operator=\"out\" result=\"low\"/>" > file
    print "    <feGaussianBlur in=\"low\" stdDeviation=\"1.80\"/>" > file
    print "    <feComposite in2=\"SourceAlpha\" operator=\"in\" result=\"lowin\"/>" > file
    print "    <feFlood flood-color=\"#5D626A\" flood-opacity=\"0.6\"/>" > file
    print "    <feComposite in2=\"lowin\" operator=\"in\" result=\"shadow\"/>" > file
    print "    <feOffset in=\"SourceAlpha\" dx=\"2.5\" dy=\"3.0\" result=\"dn\"/>" > file
    print "    <feComposite in=\"SourceAlpha\" in2=\"dn\" operator=\"out\" result=\"high\"/>" > file
    print "    <feGaussianBlur in=\"high\" stdDeviation=\"1.20\"/>" > file
    print "    <feComposite in2=\"SourceAlpha\" operator=\"in\" result=\"highin\"/>" > file
    print "    <feFlood flood-color=\"#FFFFFF\" flood-opacity=\"0.7\"/>" > file
    print "    <feComposite in2=\"highin\" operator=\"in\" result=\"light\"/>" > file
    print "    <feMerge><feMergeNode in=\"line\"/><feMergeNode in=\"SourceGraphic\"/><feMergeNode in=\"shadow\"/><feMergeNode in=\"light\"/></feMerge>" > file
    print "  </filter>" > file
    print "  <filter id=\"inkGold\" x=\"-25%\" y=\"-25%\" width=\"150%\" height=\"150%\" color-interpolation-filters=\"sRGB\">" > file
    print "    <feMorphology in=\"SourceAlpha\" operator=\"dilate\" radius=\"2.0\" result=\"grow\"/>" > file
    print "    <feGaussianBlur in=\"grow\" stdDeviation=\"0.3\" result=\"growsoft\"/>" > file
    print "    <feFlood flood-color=\"#3A2306\"/>" > file
    print "    <feComposite in2=\"growsoft\" operator=\"in\" result=\"line\"/>" > file
    print "    <feOffset in=\"SourceAlpha\" dx=\"-3.0\" dy=\"-5.0\" result=\"up\"/>" > file
    print "    <feComposite in=\"SourceAlpha\" in2=\"up\" operator=\"out\" result=\"low\"/>" > file
    print "    <feGaussianBlur in=\"low\" stdDeviation=\"2.25\"/>" > file
    print "    <feComposite in2=\"SourceAlpha\" operator=\"in\" result=\"lowin\"/>" > file
    print "    <feFlood flood-color=\"#8A5A12\" flood-opacity=\"0.55\"/>" > file
    print "    <feComposite in2=\"lowin\" operator=\"in\" result=\"shadow\"/>" > file
    print "    <feOffset in=\"SourceAlpha\" dx=\"2.5\" dy=\"3.0\" result=\"dn\"/>" > file
    print "    <feComposite in=\"SourceAlpha\" in2=\"dn\" operator=\"out\" result=\"high\"/>" > file
    print "    <feGaussianBlur in=\"high\" stdDeviation=\"1.20\"/>" > file
    print "    <feComposite in2=\"SourceAlpha\" operator=\"in\" result=\"highin\"/>" > file
    print "    <feFlood flood-color=\"#FFF0B8\" flood-opacity=\"0.6\"/>" > file
    print "    <feComposite in2=\"highin\" operator=\"in\" result=\"light\"/>" > file
    print "    <feMerge><feMergeNode in=\"line\"/><feMergeNode in=\"SourceGraphic\"/><feMergeNode in=\"shadow\"/><feMergeNode in=\"light\"/></feMerge>" > file
    print "  </filter>" > file
    print "  <filter id=\"inkSteam\" x=\"-25%\" y=\"-25%\" width=\"150%\" height=\"150%\" color-interpolation-filters=\"sRGB\">" > file
    print "    <feMorphology in=\"SourceAlpha\" operator=\"dilate\" radius=\"1.6\" result=\"grow\"/>" > file
    print "    <feGaussianBlur in=\"grow\" stdDeviation=\"0.3\" result=\"growsoft\"/>" > file
    print "    <feFlood flood-color=\"#3E4249\"/>" > file
    print "    <feComposite in2=\"growsoft\" operator=\"in\" result=\"line\"/>" > file
    print "    <feOffset in=\"SourceAlpha\" dx=\"-3.0\" dy=\"-4.0\" result=\"up\"/>" > file
    print "    <feComposite in=\"SourceAlpha\" in2=\"up\" operator=\"out\" result=\"low\"/>" > file
    print "    <feGaussianBlur in=\"low\" stdDeviation=\"1.80\"/>" > file
    print "    <feComposite in2=\"SourceAlpha\" operator=\"in\" result=\"lowin\"/>" > file
    print "    <feFlood flood-color=\"#A7AEB8\" flood-opacity=\"0.45\"/>" > file
    print "    <feComposite in2=\"lowin\" operator=\"in\" result=\"shadow\"/>" > file
    print "    <feOffset in=\"SourceAlpha\" dx=\"2.0\" dy=\"2.0\" result=\"dn\"/>" > file
    print "    <feComposite in=\"SourceAlpha\" in2=\"dn\" operator=\"out\" result=\"high\"/>" > file
    print "    <feGaussianBlur in=\"high\" stdDeviation=\"0.80\"/>" > file
    print "    <feComposite in2=\"SourceAlpha\" operator=\"in\" result=\"highin\"/>" > file
    print "    <feFlood flood-color=\"#FFFFFF\" flood-opacity=\"0.0\"/>" > file
    print "    <feComposite in2=\"highin\" operator=\"in\" result=\"light\"/>" > file
    print "    <feMerge><feMergeNode in=\"line\"/><feMergeNode in=\"SourceGraphic\"/><feMergeNode in=\"shadow\"/><feMergeNode in=\"light\"/></feMerge>" > file
    print "  </filter>" > file
    print "  <filter id=\"contact\" x=\"-30%\" y=\"-30%\" width=\"160%\" height=\"180%\" color-interpolation-filters=\"sRGB\">" > file
    print "    <feGaussianBlur in=\"SourceAlpha\" stdDeviation=\"3.0\"/>" > file
    print "    <feOffset dx=\"0\" dy=\"4.0\" result=\"b\"/>" > file
    print "    <feFlood flood-color=\"#000\" flood-opacity=\"0.55\"/>" > file
    print "    <feComposite in2=\"b\" operator=\"in\" result=\"s\"/>" > file
    print "    <feMerge><feMergeNode in=\"s\"/><feMergeNode in=\"SourceGraphic\"/></feMerge>" > file
    print "  </filter>" > file
    print "  <filter id=\"lift\" x=\"-30%\" y=\"-30%\" width=\"160%\" height=\"180%\" color-interpolation-filters=\"sRGB\">" > file
    print "    <feGaussianBlur in=\"SourceAlpha\" stdDeviation=\"5.0\"/>" > file
    print "    <feOffset dx=\"0\" dy=\"5.0\" result=\"b\"/>" > file
    print "    <feFlood flood-color=\"#000\" flood-opacity=\"0.5\"/>" > file
    print "    <feComposite in2=\"b\" operator=\"in\" result=\"s\"/>" > file
    print "    <feMerge><feMergeNode in=\"s\"/><feMergeNode in=\"SourceGraphic\"/></feMerge>" > file
    print "  </filter>" > file
    print "  <radialGradient id=\"redSkin\" cx=\"0.38\" cy=\"0.32\" r=\"0.75\">" > file
    print "    <stop offset=\"0\" stop-color=\"#EE4249\"/><stop offset=\"0.6\" stop-color=\"#D7262E\"/><stop offset=\"1\" stop-color=\"#B91C24\"/>" > file
    print "  </radialGradient>" > file
    print "  <linearGradient id=\"hornG\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\">" > file
    print "    <stop offset=\"0\" stop-color=\"#EEF0F3\"/><stop offset=\"1\" stop-color=\"#9DA2AA\"/>" > file
    print "  </linearGradient>" > file
    print "  <radialGradient id=\"irisG\" cx=\"0.4\" cy=\"0.3\" r=\"0.8\">" > file
    print "    <stop offset=\"0\" stop-color=\"#FBE59A\"/><stop offset=\"0.7\" stop-color=\"#E9C766\"/><stop offset=\"1\" stop-color=\"#C79A2E\"/>" > file
    print "  </radialGradient>" > file
    print "  <linearGradient id=\"puffG\" x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\">" > file
    print "    <stop offset=\"0\" stop-color=\"#FFFFFF\"/><stop offset=\"1\" stop-color=\"#D5D9DF\"/>" > file
    print "  </linearGradient>" > file
    print "  <linearGradient id=\"bodyG\" x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\">" > file
    print "    <stop offset=\"0\" stop-color=\"#1D1E23\"/><stop offset=\"1\" stop-color=\"#050506\"/>" > file
    print "  </linearGradient>" > file
    print "  <linearGradient id=\"screenG\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\">" > file
    print "    <stop offset=\"0\" stop-color=\"#23242C\"/><stop offset=\"1\" stop-color=\"#0C0C10\"/>" > file
    print "  </linearGradient>" > file
    print "  <linearGradient id=\"rimG\" x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\">" > file
    print "    <stop offset=\"0\" stop-color=\"#FFFFFF\"/><stop offset=\"1\" stop-color=\"#D3D6DC\"/>" > file
    print "  </linearGradient>" > file
    print "  <clipPath id=\"bootScreen\"><rect x=\"404.5\" y=\"449.5\" width=\"217\" height=\"127\" rx=\"10.5\"/></clipPath>" > file
    print "  </defs>" > file
}

# Body, wings, tail and head: everything the handheld hides or that rises above its top edge.
function behind(file, t,    a) {
    print "    <g filter=\"url(#inkRed)\">" > file
    print "      <ellipse cx=\"480\" cy=\"300\" rx=\"120\" ry=\"70\" fill=\"url(#redSkin)\"/>" > file
    print "    </g>" > file
    print "    <g filter=\"url(#inkGold)\">" > file
    printf "      <ellipse cx=\"480\" cy=\"318\" rx=\"70\" ry=\"40\" fill=\"%s\"/>\n", GOLD > file
    print "    </g>" > file
    wing(file, "translate(404 228) scale(-0.62 0.62) rotate(-18)", "url(#redSkin)", SILVER, "inkRed")
    wing(file, "translate(500 226) scale(0.5) rotate(-40)", DARKRED, DARKSILVER, "inkDark")
    # the tail flicks a few degrees about its root in the body; the root shows while the
    # handheld is edge-on, so the tail never floats free of the dragon
    a = 5 * sin(2 * pi * t)
    printf "    <g transform=\"rotate(%.2f 600 300)\">\n", a > file
    print "      <path d=\"M590,300 L640,300 C700,300 720,270 734,246\" fill=\"none\" stroke=\"#2A0508\" stroke-width=\"15\" stroke-linecap=\"round\"/>" > file
    printf "      <path d=\"M590,300 L640,300 C700,300 720,270 734,246\" fill=\"none\" stroke=\"%s\" stroke-width=\"10\" stroke-linecap=\"round\"/>\n", RED > file
    print "      <path d=\"M600,297 L640,297 C694,297 712,270 726,250\" fill=\"none\" stroke=\"#FF9C8F\" stroke-opacity=\"0.45\" stroke-width=\"2.5\" stroke-linecap=\"round\"/>" > file
    print "      <g filter=\"url(#inkGold)\">" > file
    printf "        <path d=\"M730,252 L742,222 L754,246 Q742,240 730,252 Z\" fill=\"%s\"/>\n", GOLD > file
    print "      </g>" > file
    print "    </g>" > file
    print "    <g transform=\"translate(0 12)\">" > file
    head(file)
    steam(file, t)
    print "    </g>" > file
}

function wing(file, transform, fill, bone, ink) {
    printf "    <g transform=\"%s\">\n", transform > file
    printf "      <g filter=\"url(#%s)\">\n", ink > file
    printf "      <path d=\"M0,0 C6,-44 30,-84 72,-104 Q80,-74 110,-64 Q94,-40 118,-22 Q80,-26 60,-6 Q30,-14 0,0 Z\" fill=\"%s\"/>\n", fill > file
    print "      </g>" > file
    printf "      <path d=\"M0,0 L30,-58 L72,-104 M30,-58 L110,-64 M30,-58 L118,-22\" fill=\"none\" stroke=\"%s\" stroke-width=\"3\" stroke-linecap=\"round\"/>\n", bone > file
    print "    </g>" > file
}

function head(file) {
    print "      <g filter=\"url(#inkSilver)\">" > file
    print "        <path d=\"M440,140 C430,118 412,108 396,110 C410,118 420,130 426,146 Z\" fill=\"url(#hornG)\"/>" > file
    print "        <path d=\"M478,132 C476,110 466,96 452,90 C462,104 466,118 464,136 Z\" fill=\"url(#hornG)\"/>" > file
    print "      </g>" > file
    print "      <path d=\"M428,128 C422,120 414,116 406,114 M468,118 C466,110 462,104 457,98\" fill=\"none\" stroke=\"#fff\" stroke-opacity=\"0.75\" stroke-width=\"2\" stroke-linecap=\"round\"/>" > file
    print "      <g filter=\"url(#inkDark)\">" > file
    print "        <path d=\"M420,170 L388,156 L404,176 L386,186 L418,190 Z\" fill=\"#8A1520\"/>" > file
    print "      </g>" > file
    print "      <g filter=\"url(#inkRed)\">" > file
    print "        <ellipse cx=\"470\" cy=\"180\" rx=\"58\" ry=\"50\" fill=\"url(#redSkin)\"/>" > file
    print "        <ellipse cx=\"522\" cy=\"196\" rx=\"34\" ry=\"24\" fill=\"url(#redSkin)\"/>" > file
    print "      </g>" > file
    print "      <path d=\"M505,186 C508,193 508,200 505,207\" fill=\"none\" stroke=\"#8A1520\" stroke-opacity=\"0.45\" stroke-width=\"2.5\" stroke-linecap=\"round\"/>" > file
    print "      <ellipse cx=\"452\" cy=\"148\" rx=\"16\" ry=\"7\" transform=\"rotate(-24 452 148)\" fill=\"#fff\" fill-opacity=\"0.22\"/>" > file
    print "      <ellipse cx=\"482\" cy=\"195\" rx=\"9\" ry=\"5\" fill=\"#FF8FA3\" fill-opacity=\"0.35\"/>" > file
    print "      <path d=\"M486,148 C496,144 508,148 514,156\" fill=\"none\" stroke=\"#6E0F18\" stroke-width=\"4\" stroke-linecap=\"round\"/>" > file
    print "      <circle cx=\"490\" cy=\"168\" r=\"13\" fill=\"url(#irisG)\" stroke=\"#3A0A0E\" stroke-width=\"2.2\"/>" > file
    print "      <ellipse cx=\"492\" cy=\"168\" rx=\"4\" ry=\"9\" fill=\"#120404\"/>" > file
    print "      <circle cx=\"496\" cy=\"162\" r=\"3\" fill=\"#fff\"/>" > file
    print "      <circle cx=\"486.5\" cy=\"174\" r=\"1.4\" fill=\"#fff\" fill-opacity=\"0.85\"/>" > file
    print "      <ellipse cx=\"546\" cy=\"188\" rx=\"3.2\" ry=\"2.2\" fill=\"#3A0A0E\"/>" > file
    print "      <path d=\"M500,210 Q526,220 552,203\" fill=\"none\" stroke=\"#4A0A10\" stroke-width=\"3\" stroke-linecap=\"round\"/>" > file
    print "      <path d=\"M528,214 L532,223 L536,212 Z\" fill=\"#fff\" stroke=\"#4A0A10\" stroke-width=\"1\" stroke-linejoin=\"round\"/>" > file
    print "      <path d=\"M440,212 C450,206 458,206 466,210\" fill=\"none\" stroke=\"#D4A64A\" stroke-width=\"5\" stroke-linecap=\"round\"/>" > file
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
        printf "      <g fill=\"url(#puffG)\" opacity=\"%.3f\">\n", o > file
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
    print "    <rect x=\"286.5\" y=\"410.5\" width=\"452\" height=\"205\" rx=\"78.5\" fill=\"url(#bodyG)\" stroke=\"url(#rimG)\" stroke-width=\"7\"/>" > file
    print "    <rect x=\"296\" y=\"420\" width=\"433\" height=\"186\" rx=\"69\" fill=\"none\" stroke=\"#fff\" stroke-opacity=\"0.10\" stroke-width=\"2\"/>" > file
    print "    <path d=\"M370,420 Q512.5,414 655,420\" fill=\"none\" stroke=\"#fff\" stroke-opacity=\"0.12\" stroke-width=\"2.5\" stroke-linecap=\"round\"/>" > file
    print "    <rect x=\"404.5\" y=\"449.5\" width=\"217\" height=\"127\" rx=\"10.5\" fill=\"url(#screenG)\"/>" > file
    print "    <g clip-path=\"url(#bootScreen)\">" > file
    print "      <path d=\"M452,440 L522,440 L452,586 L382,586 Z\" fill=\"#fff\" fill-opacity=\"0.07\"/>" > file
    print "      <path d=\"M532,440 L557,440 L487,586 L462,586 Z\" fill=\"#fff\" fill-opacity=\"0.05\"/>" > file
    print "    </g>" > file
    print "    <rect x=\"404.5\" y=\"449.5\" width=\"217\" height=\"127\" rx=\"10.5\" fill=\"none\" stroke=\"url(#rimG)\" stroke-width=\"5\"/>" > file
    printf "    <rect x=\"%.1f\" y=\"%.1f\" width=\"46\" height=\"14\" rx=\"2.5\" fill=\"url(#rimG)\"/>\n", dx - 23, dy - 7 > file
    printf "    <rect x=\"%.1f\" y=\"%.1f\" width=\"14\" height=\"46\" rx=\"2.5\" fill=\"url(#rimG)\"/>\n", dx - 7, dy - 23 > file
    print "    <circle cx=\"679\" cy=\"456.5\" r=\"7\" fill=\"url(#rimG)\"/>" > file
    print "    <circle cx=\"660.9\" cy=\"474.7\" r=\"7\" fill=\"url(#rimG)\"/>" > file
    print "    <circle cx=\"697.1\" cy=\"474.6\" r=\"7\" fill=\"url(#rimG)\"/>" > file
    print "    <circle cx=\"679.1\" cy=\"492.7\" r=\"7\" fill=\"url(#rimG)\"/>" > file
    printf "    <circle cx=\"%.1f\" cy=\"%.1f\" r=\"18.7\" fill=\"#141519\" stroke=\"url(#rimG)\" stroke-width=\"5\"/>\n", sx, sy > file
    print "    <circle cx=\"679\" cy=\"557.5\" r=\"18.7\" fill=\"#141519\" stroke=\"url(#rimG)\" stroke-width=\"5\"/>" > file
    printf "    <circle cx=\"%.1f\" cy=\"%.1f\" r=\"5\" fill=\"#fff\"/>\n", sx, sy > file
    print "    <circle cx=\"679\" cy=\"557.5\" r=\"5\" fill=\"#fff\"/>" > file
    print "  </g>" > file
}

# The front paws hook over the rim and ride its turning edge inward; they keep their own shape.
function paws(file, sx,    i, px) {
    print "    <g filter=\"url(#contact)\"><g filter=\"url(#inkRed)\">" > file
    for (i = 0; i < 2; i++) {
        px = AXIS + ((i ? 540 : 420) - AXIS) * sx
        printf "      <ellipse cx=\"%.2f\" cy=\"236\" rx=\"22\" ry=\"11\" fill=\"url(#redSkin)\"/>\n", px > file
    }
    print "    </g></g>" > file
    # each claw is a light stroke over a dark one, the ink line the filters give the paws
    for (i = 0; i < 2; i++) {
        px = AXIS + ((i ? 540 : 420) - AXIS) * sx
        printf "    <path d=\"M%.2f,243 l-2,10 M%.2f,246 l-1,11 M%.2f,244 l1,10\" fill=\"none\" stroke=\"#1C1D21\" stroke-width=\"6\" stroke-linecap=\"round\"/>\n", \
            px - 14, px - 2, px + 10 > file
        printf "    <path d=\"M%.2f,243 l-2,10 M%.2f,246 l-1,11 M%.2f,244 l1,10\" fill=\"none\" stroke=\"%s\" stroke-width=\"3.5\" stroke-linecap=\"round\"/>\n", \
            px - 14, px - 2, px + 10, CLAW > file
    }
}
