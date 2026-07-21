import cv2


image_path = "fiche2.png"

image = cv2.imread(image_path)


def mouse_callback(event, x, y, flags, param):

    if event == cv2.EVENT_LBUTTONDOWN:

        print(
            f"X = {x}, Y = {y}"
        )


cv2.namedWindow("Image")

cv2.setMouseCallback(
    "Image",
    mouse_callback
)


while True:

    cv2.imshow(
        "Image",
        image
    )

    key = cv2.waitKey(1)

    if key == 27:  # ESC

        break


cv2.destroyAllWindows()