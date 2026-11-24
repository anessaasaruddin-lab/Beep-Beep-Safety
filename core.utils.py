def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    current = ""
    for w in words:
        test = current + w + " "
        if font.size(test)[0] <= max_width:
            current = test
        else:
            lines.append(current.strip())
            current = w + " "
    if current.strip():
        lines.append(current.strip())
    return lines


def draw_text_lines(text, font, color, surface, x, y, max_width):
    lines = wrap_text(text, font, max_width)
    yy = y
    for line in lines:
        surf = font.render(line, True, color)
        surface.blit(surf, (x, yy))
        yy += font.get_linesize()
