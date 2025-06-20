const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const imagenInput = document.getElementById("imagenInput");
const formulario = document.getElementById("formulario");
const camaraSeccion = document.getElementById("camaraSeccion");
const previewImg = document.getElementById("previewImg");
const modoCamaraBtn = document.getElementById("modoCamaraBtn");
const modoArchivoBtn = document.getElementById("modoArchivoBtn");
const resultadosCamara = document.getElementById("resultadosCamara");
const infoResiduos = document.getElementById("infoResiduos");
const clasificarBtn = document.getElementById("clasificarBtn");

let usarCamara = false;
let stream = null;
let deteccionInterval = null;

canvas.style.position = 'absolute';
canvas.style.top = '0';
canvas.style.left = '0';
canvas.style.pointerEvents = 'none';

modoCamaraBtn.addEventListener("click", () => {
  usarCamara = true;
  camaraSeccion.style.display = "block";
  previewImg.style.display = "none";
  clasificarBtn.innerHTML = "📷";
  navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
    .then((s) => {
      stream = s;
      video.srcObject = stream;
      video.onloadedmetadata = () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        startDeteccionTiempoReal();
      };
    })
    .catch((err) => {
      console.error("Error al acceder a la cámara:", err);
      resultadosCamara.innerHTML = `<p id="textoResultados">Error al acceder a la cámara: ${err.message}</p>`;
      alert("No se pudo acceder a la cámara: " + err.message);
    });
});

modoArchivoBtn.addEventListener("click", () => {
  usarCamara = false;
  camaraSeccion.style.display = "none";
  clasificarBtn.innerHTML = "Clasificar";
  if (stream) stream.getTracks().forEach((t) => t.stop());
  if (deteccionInterval) clearInterval(deteccionInterval);
  imagenInput.click();
});

imagenInput.addEventListener("change", function () {
  const file = this.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function (e) {
      previewImg.src = e.target.result;
      previewImg.style.display = "block";
      camaraSeccion.style.display = "none";
      clasificarBtn.innerHTML = "Clasificar";
    };
    reader.readAsDataURL(file);
  }
});

formulario.addEventListener("submit", function (e) {
  if (usarCamara) {
    e.preventDefault();
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);
    canvas.toBlob(function (blob) {
      const file = new File([blob], "captura.jpg", { type: "image/jpeg" });
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(file);
      imagenInput.files = dataTransfer.files;
      formulario.submit();
    }, "image/jpeg", 0.7);
  }
});

function startDeteccionTiempoReal() {
  if (deteccionInterval) clearInterval(deteccionInterval);
  deteccionInterval = setInterval(() => {
    if (!video.srcObject || video.paused || video.ended) {
      console.warn("Video no está activo, deteniendo detección.");
      resultadosCamara.innerHTML = `<p id="textoResultados">Video no activo. Por favor, reinicia la cámara.</p>`;
      clearInterval(deteccionInterval);
      return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      const reader = new FileReader();
      reader.onload = function () {
        fetch(window.procesarFrameUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": window.csrfToken,
          },
          body: "frame=" + encodeURIComponent(reader.result),
        })
          .then((response) => {
            if (!response.ok) {
              throw new Error(`Error HTTP: ${response.status} ${response.statusText}`);
            }
            return response.json();
          })
          .then((data) => {
            console.log("Respuesta del servidor:", data);
            resultadosCamara.innerHTML = "";
            infoResiduos.innerHTML = "";
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            if (data.error) {
              console.error("Error del servidor:", data.error);
              resultadosCamara.innerHTML = `<p id="textoResultados">Error del servidor: ${data.error}</p>`;
              return;
            }

            if (data.detecciones && data.detecciones.length > 0) {
              ctx.strokeStyle = "lime";
              ctx.lineWidth = 2;
              ctx.font = "20px Arial";
              ctx.fillStyle = "lime";

              const residuosAgrupados = {};
              data.detecciones.forEach((det) => {
                const clase = det.clase.toLowerCase();
                if (!residuosAgrupados[clase]) {
                  residuosAgrupados[clase] = { confidences: [], boxes: [] };
                }
                residuosAgrupados[clase].confidences.push(det.confidence);
                residuosAgrupados[clase].boxes.push(det.box);

                const [x_min, y_min, x_max, y_max] = det.box;
                const label = `${det.clase} (${(det.confidence * 100).toFixed(1)}%)`;
                ctx.strokeRect(x_min, y_min, x_max - x_min, y_max - y_min);
                ctx.fillText(label, x_min, y_min - 10);
              });

              Object.keys(residuosAgrupados).forEach((clase) => {
                const confidences = residuosAgrupados[clase].confidences;
                // Calcular confianza promedio
                const avgConfidence = confidences.reduce((a, b) => a + b, 0) / confidences.length;
                const confPercent = (avgConfidence * 100).toFixed(1);

                if (clase === "plastico" && window.staticImages.plastico) {
                  resultadosCamara.innerHTML += `<img src="${window.staticImages.plastico}" alt="plástico" class="residuo-img"/>`;
                  infoResiduos.innerHTML += `
                    <p><strong>Tipo:</strong> Plástico (Confianza: ${confPercent}%)</p>
                    <p><strong>Tiempo de degradación:</strong> 100-1000 años</p>
                    <p><strong>Impacto ambiental:</strong> Los plásticos contribuyen a la contaminación de océanos y suelos, afectando la fauna marina y terrestre. Microplásticos ingeridos por animales pueden entrar en la cadena alimenticia, impactando la salud humana.</p>
                    <p><strong>Recomendación de reciclaje:</strong> Separa botellas, envases y bolsas plásticas, límpialos y deposítalos en contenedores de reciclaje. Evita plásticos de un solo uso.</p>
                    <hr/>
                  `;
                } else if (clase === "papel" && window.staticImages.papel) {
                  resultadosCamara.innerHTML += `<img src="${window.staticImages.papel}" alt="papel" class="residuo-img"/>`;
                  infoResiduos.innerHTML += `
                    <p><strong>Tipo:</strong> Papel (Confianza: ${confPercent}%)</p>
                    <p><strong>Tiempo de degradación:</strong> 2-6 semanas</p>
                    <p><strong>Impacto ambiental:</strong> La producción de papel consume grandes cantidades de agua y energía, y contribuye a la deforestación. El reciclaje reduce la necesidad de talar árboles y el uso de recursos.</p>
                    <p><strong>Recomendación de reciclaje:</strong> Recicla papel limpio y seco, como periódicos, cartones y hojas. Evita mezclar con residuos orgánicos.</p>
                    <hr/>
                  `;
                } else if (clase === "vidrio" && window.staticImages.vidrio) {
                  resultadosCamara.innerHTML += `<img src="${window.staticImages.vidrio}" alt="vidrio" class="residuo-img"/>`;
                  infoResiduos.innerHTML += `
                    <p><strong>Tipo:</strong> Vidrio (Confianza: ${confPercent}%)</p>
                    <p><strong>Tiempo de degradación:</strong> Indefinido (miles de años)</p>
                    <p><strong>Impacto ambiental:</strong> Aunque no libera toxinas, el vidrio desechado ocupa espacio en vertederos. Su reciclaje es altamente eficiente, ya que puede reutilizarse infinitamente sin pérdida de calidad.</p>
                    <p><strong>Recomendación de reciclaje:</strong> Lava y separa botellas y frascos de vidrio por color (si aplica) y deposítalos en contenedores específicos.</p>
                    <hr/>
                  `;
                } else if (clase === "metal" && window.staticImages.metal) {
                  resultadosCamara.innerHTML += `<img src="${window.staticImages.metal}" alt="metal" class="residuo-img"/>`;
                  infoResiduos.innerHTML += `
                    <p><strong>Tipo:</strong> Metal (Confianza: ${confPercent}%)</p>
                    <p><strong>Tiempo de degradación:</strong> 50-500 años</p>
                    <p><strong>Impacto ambiental:</strong> La extracción de metales agota recursos naturales y genera contaminación. Metales desechados pueden liberar sustancias tóxicas en el suelo y agua.</p>
                    <p><strong>Recomendación de reciclaje:</strong> Recicla latas, envases y objetos metálicos. Asegúrate de limpiarlos para facilitar el proceso de reciclaje.</p>
                    <hr/>
                  `;
                } else {
                  resultadosCamara.innerHTML += `<p>No se tiene imagen para este tipo de residuo: ${clase}</p>`;
                  infoResiduos.innerHTML += `
                    <p>No se tiene información detallada para el residuo: ${clase} (Confianza: ${confPercent}%)</p>
                    <p><strong>Recomendación:</strong> Consulta con tu centro de reciclaje local para clasificar correctamente este material.</p>
                    <hr/>
                  `;
                }
              });
            } else {
              resultadosCamara.innerHTML = `<p id="textoResultados">No se detectaron residuos.</p>`;
              infoResiduos.innerHTML = `<p>No se tiene información para este tipo de residuo.</p>`;
            }
          })
          .catch((error) => {
            console.error("Error al procesar frame:", error);
            resultadosCamara.innerHTML = `<p id="textoResultados">Error al procesar frame: ${error.message}</p>`;
            infoResiduos.innerHTML = `<p>Error al obtener información: ${error.message}</p>`;
          });
      };
      reader.readAsDataURL(blob);
    }, "image/jpeg", 0.7);
  }, 300);
}