try:
    supershape = ximport("supershape")
except:
    supershape = ximport("__init__")
    reload(supershape)

size(400, 400)

nofill()
stroke(0)

font("Times", 100)
path = textpath("FUN!", 100, 150)

for contour in path.contours:
    contour = supershape.transform(contour, 50, 0.25, 3.5, 3.5)
    drawpath(contour)
