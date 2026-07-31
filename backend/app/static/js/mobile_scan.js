const input = document.getElementById("imageInput");
const preview = document.getElementById("preview");
const upload = document.getElementById("uploadButton");

const sessionId = window.location.pathname.split("/").pop();

input.addEventListener("change", () => {

    if (input.files.length === 0)
        return;

    preview.src = URL.createObjectURL(input.files[0]);

    preview.style.display = "block";

    upload.disabled = false;

});


upload.addEventListener("click", async () => {

    const file = input.files[0];

    if (!file)
        return;

    upload.disabled = true;

    upload.innerText = "Envoi...";

    const formData = new FormData();

    formData.append("image", file);

    try {

        const response = await fetch(
            "/scan/upload/" + sessionId,
            {
                method: "POST",
                body: formData
            }
        );

        const result = await response.json();

        upload.innerText = "✅ Envoyé";

        alert("Image envoyée avec succès.");

        console.log(result);

    }
    catch (e) {

        console.error(e);

        upload.innerText = "☁ Envoyer";

        upload.disabled = false;

        alert("Erreur lors de l'envoi.");

    }

});