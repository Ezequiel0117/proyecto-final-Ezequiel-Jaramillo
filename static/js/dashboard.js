// 🌿 Dashboard EcoSoft - JavaScript
// Universidad Nacional de Educación (UNEMI) 2025

document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard EcoSoft cargado correctamente');
    
    // Verificar si el usuario está autenticado
    const titleBanner = document.querySelector('.titulo-banner');
    if (!titleBanner) {
        console.log('Usuario no autenticado - Dashboard público');
        return;
    }

    // Cargar datos del dashboard para usuarios autenticados
    cargarDatosDashboard();
});

function cargarDatosDashboard() {
    console.log('Iniciando carga de datos del dashboard...');
    
    fetch("/api/metricas/")
        .then((response) => {
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then((data) => {
            console.log("Datos recibidos de /api/metricas/:", data);

            if (data.error) {
                mostrarError(data.error);
                return;
            }

            const resumen = data.resumen;
            const impacto = data.impacto;
            const progreso = data.progreso;

            // Verificar si hay datos para mostrar
            if (resumen.residuos_clasificados === 0) {
                mostrarMensajeSinDatos();
                return;
            }

            // Generar los gráficos
            crearGraficoResumen(resumen);
            crearGraficoImpacto(impacto);
            crearBarraProgreso(progreso);

            console.log('Dashboard cargado exitosamente');
        })
        .catch((error) => {
            console.error("Error al cargar los datos:", error);
            mostrarError("Error al conectar con el servidor. Por favor, intenta más tarde.");
        });
}

function mostrarError(mensaje) {
    const container = document.querySelector('.dashboard-container');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-triangle"></i>
        <p>${mensaje}</p>
    `;
    container.appendChild(errorDiv);
}

function mostrarMensajeSinDatos() {
    const container = document.querySelector('.dashboard-container');
    const noDataDiv = document.createElement('div');
    noDataDiv.className = 'no-data-message';
    noDataDiv.innerHTML = `
        <i class="fas fa-info-circle"></i>
        <h3>¡Comienza tu viaje ecológico!</h3>
        <p>No hay residuos clasificados en los últimos 30 días.</p>
        <p>¡Sube una imagen para comenzar a contribuir al medio ambiente!</p>
        <a href="/clasificar/" class="btn-primary">
            <i class="fas fa-camera"></i> Clasificar Residuos
        </a>
    `;
    container.appendChild(noDataDiv);
}

function crearGraficoResumen(resumen) {
    console.log('Creando gráfico de resumen mensual...');
    
    // Limpiar contenedor previo
    d3.select("#grafico-resumen").selectAll("*").remove();
    
    const datosResumen = [
        { tipo: "Plástico", valor: resumen.plasticos || 0, color: "#4CAF50", icon: "🔸" },
        { tipo: "Papel", valor: resumen.papel || 0, color: "#81C784", icon: "📄" },
        { tipo: "Vidrio", valor: resumen.vidrio || 0, color: "#AED581", icon: "🔹" },
        { tipo: "Metal", valor: resumen.metal || 0, color: "#C8E6C9", icon: "⚙️" }
    ];

    // Filtrar datos con valores mayores a 0
    const datosConValores = datosResumen.filter(d => d.valor > 0);
    
    if (datosConValores.length === 0) {
        d3.select("#grafico-resumen")
            .append("p")
            .attr("class", "no-data-message")
            .text("No hay datos de clasificación para mostrar");
        return;
    }

    // Configuración del SVG
    const containerWidth = document.getElementById('grafico-resumen').clientWidth || 400;
    const svgWidth = Math.min(containerWidth, 450);
    const svgHeight = 280;
    const margin = { top: 20, right: 30, bottom: 40, left: 100 };
    const width = svgWidth - margin.left - margin.right;
    const height = svgHeight - margin.top - margin.bottom;

    const svg = d3.select("#grafico-resumen")
        .append("svg")
        .attr("width", svgWidth)
        .attr("height", svgHeight)
        .attr("viewBox", `0 0 ${svgWidth} ${svgHeight}`)
        .attr("preserveAspectRatio", "xMidYMid meet");

    const g = svg.append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Escalas
    const x = d3.scaleLinear()
        .domain([0, d3.max(datosConValores, d => d.valor) * 1.1])
        .range([0, width]);

    const y = d3.scaleBand()
        .domain(datosConValores.map(d => d.tipo))
        .range([0, height])
        .padding(0.3);

    // Crear barras con animación
    const barras = g.selectAll(".bar")
        .data(datosConValores)
        .enter()
        .append("g")
        .attr("class", "bar-group");

    barras.append("rect")
        .attr("class", "bar")
        .attr("x", 0)
        .attr("y", d => y(d.tipo))
        .attr("width", 0)
        .attr("height", y.bandwidth())
        .attr("fill", d => d.color)
        .attr("rx", 5)
        .attr("ry", 5)
        .transition()
        .duration(1000)
        .delay((d, i) => i * 200)
        .attr("width", d => x(d.valor));

    // Etiquetas de valores
    barras.append("text")
        .attr("class", "bar-label")
        .attr("x", d => x(d.valor) + 5)
        .attr("y", d => y(d.tipo) + y.bandwidth() / 2)
        .attr("dy", ".35em")
        .attr("font-size", "12px")
        .attr("font-weight", "600")
        .attr("fill", "#333")
        .style("opacity", 0)
        .text(d => `${d.valor} kg`)
        .transition()
        .duration(1000)
        .delay((d, i) => i * 200 + 500)
        .style("opacity", 1);

    // Eje X
    g.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x).ticks(5).tickFormat(d => `${d} kg`))
        .selectAll("text")
        .attr("font-size", "10px")
        .attr("fill", "#666");

    // Eje Y con iconos
    const yAxis = g.append("g")
        .call(d3.axisLeft(y))
        .selectAll("text")
        .attr("font-size", "12px")
        .attr("fill", "#333")
        .attr("font-weight", "500");
}

function crearGraficoImpacto(impacto) {
    console.log('Creando gráfico de impacto ecológico...');
    
    // Limpiar contenedores previos
    d3.select("#grafico-impacto").selectAll("*").remove();
    d3.select("#legend-impacto").selectAll("*").remove();
    
    const datosImpacto = [
        { 
            label: "CO₂ Evitado", 
            value: parseFloat(impacto.co2_ev) || 0, 
            color: "#4CAF50",
            unit: " kg",
            icon: "🌱"
        },
        { 
            label: "Árboles Salvados", 
            value: parseInt(impacto.arboles) || 0, 
            color: "#81C784",
            unit: "",
            icon: "🌳"
        },
        { 
            label: "Kg sin Degradación", 
            value: parseFloat(impacto.degradacion) || 0, 
            color: "#AED581",
            unit: " kg",
            icon: "♻️"
        },
        { 
            label: "Mejora Ambiental", 
            value: parseFloat(impacto.mejora) || 0, 
            color: "#C8E6C9",
            unit: "%",
            icon: "📈"
        }
    ];

    // Filtrar datos con valores mayores a 0
    const datosConValores = datosImpacto.filter(d => d.value > 0);
    
    if (datosConValores.length === 0) {
        d3.select("#grafico-impacto")
            .append("p")
            .attr("class", "no-data-message")
            .text("Comienza a clasificar residuos para ver tu impacto ecológico");
        return;
    }

    // Configuración del pie chart
    const svgWidth = 300;
    const svgHeight = 250;
    const radius = Math.min(svgWidth, svgHeight) / 2 - 20;

    const svg = d3.select("#grafico-impacto")
        .append("svg")
        .attr("width", svgWidth)
        .attr("height", svgHeight)
        .attr("viewBox", `0 0 ${svgWidth} ${svgHeight}`)
        .attr("preserveAspectRatio", "xMidYMid meet");

    const g = svg.append("g")
        .attr("transform", `translate(${svgWidth/2},${svgHeight/2})`);

    // Configuración del pie
    const pie = d3.pie()
        .value(d => d.value)
        .sort(null);

    const arc = d3.arc()
        .innerRadius(radius * 0.4)
        .outerRadius(radius);

    const arcHover = d3.arc()
        .innerRadius(radius * 0.4)
        .outerRadius(radius * 1.1);

    // Crear segmentos del pie
    const arcs = g.selectAll(".arc")
        .data(pie(datosConValores))
        .enter()
        .append("g")
        .attr("class", "arc");

    arcs.append("path")
        .attr("d", arc)
        .attr("fill", d => d.data.color)
        .attr("stroke", "white")
        .attr("stroke-width", 3)
        .style("cursor", "pointer")
        .on("mouseover", function(event, d) {
            d3.select(this)
                .transition()
                .duration(200)
                .attr("d", arcHover);
        })
        .on("mouseout", function(event, d) {
            d3.select(this)
                .transition()
                .duration(200)
                .attr("d", arc);
        })
        .transition()
        .duration(1000)
        .attrTween("d", function(d) {
            const interpolate = d3.interpolate({startAngle: 0, endAngle: 0}, d);
            return function(t) {
                return arc(interpolate(t));
            };
        });

    // Crear leyenda mejorada
    const legendContainer = d3.select("#legend-impacto");
    
    datosConValores.forEach((d, i) => {
        const legendItem = legendContainer
            .append("div")
            .attr("class", "legend-item")
            .style("opacity", 0);

        legendItem.append("div")
            .attr("class", "legend-color")
            .style("background-color", d.color);

        legendItem.append("span")
            .html(`<strong>${d.label}:</strong> ${d.value}${d.unit}`);

        legendItem
            .transition()
            .duration(500)
            .delay(i * 150)
            .style("opacity", 1);
    });
}

function crearBarraProgreso(progreso) {
    console.log('Creando barra de progreso...');
    
    // Limpiar contenedor previo
    d3.select("#grafico-progreso").selectAll("*").remove();
    
    const meta = 60; // Meta mensual de residuos
    const actual = progreso.actual || 0;
    const porcentaje = Math.min(Math.round((actual / meta) * 100), 100);
    
    const container = d3.select("#grafico-progreso");
    
    // Contenedor principal de la barra
    const progressContainer = container
        .append("div")
        .attr("class", "progress-bar")
        .style("position", "relative")
        .style("width", "100%")
        .style("max-width", "500px")
        .style("margin", "0 auto");
    
    // Barra de fondo
    progressContainer
        .style("height", "40px")
        .style("background", "linear-gradient(90deg, #e0e0e0, #f5f5f5)")
        .style("border-radius", "20px")
        .style("overflow", "hidden")
        .style("box-shadow", "inset 0 2px 4px rgba(0, 0, 0, 0.1)");
    
    // Barra de progreso
    const progressFill = progressContainer
        .append("div")
        .attr("class", "progress-fill")
        .style("height", "100%")
        .style("width", "0%")
        .style("background", "linear-gradient(90deg, #4CAF50, #66BB6A, #81C784)")
        .style("border-radius", "20px")
        .style("position", "relative")
        .style("overflow", "hidden")
        .style("transition", "width 1.5s ease-in-out");
    
    // Animación de brillo
    progressFill
        .append("div")
        .style("position", "absolute")
        .style("top", "0")
        .style("left", "-100%")
        .style("width", "100%")
        .style("height", "100%")
        .style("background", "linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent)")
        .style("animation", "progressShine 2s infinite");
    
    // Texto de progreso
    const progressText = progressContainer
        .append("div")
        .attr("class", "progress-text")
        .style("position", "absolute")
        .style("top", "50%")
        .style("left", "50%")
        .style("transform", "translate(-50%, -50%)")
        .style("color", "#333")
        .style("font-weight", "600")
        .style("font-size", "1rem")
        .style("text-shadow", "0 1px 2px rgba(255, 255, 255, 0.8)")
        .style("z-index", "1")
        .text(`${porcentaje}% (${actual}/${meta} residuos)`);
    
    // Animar la barra de progreso
    setTimeout(() => {
        progressFill.style("width", `${porcentaje}%`);
    }, 500);
    
    // Estadísticas adicionales
    const statsContainer = container
        .append("div")
        .attr("class", "progress-stats")
        .style("display", "flex")
        .style("justify-content", "space-between")
        .style("margin-top", "20px")
        .style("gap", "10px");
    
    const stats = [
        { label: "Clasificados", value: actual, icon: "📊" },
        { label: "Meta Mensual", value: meta, icon: "🎯" },
        { label: "Restantes", value: Math.max(0, meta - actual), icon: "📈" }
    ];
    
    stats.forEach((stat, i) => {
        const statItem = statsContainer
            .append("div")
            .attr("class", "stat-item")
            .style("text-align", "center")
            .style("padding", "15px 10px")
            .style("background", "rgba(255, 255, 255, 0.8)")
            .style("border-radius", "10px")
            .style("flex", "1")
            .style("box-shadow", "0 2px 8px rgba(0, 0, 0, 0.1)")
            .style("opacity", "0")
            .style("transform", "translateY(20px)")
            .style("transition", "all 0.5s ease");
        
        statItem.append("div")
            .attr("class", "stat-icon")
            .style("font-size", "1.5rem")
            .style("margin-bottom", "5px")
            .text(stat.icon);
        
        statItem.append("div")
            .attr("class", "stat-value")
            .style("font-size", "1.5rem")
            .style("font-weight", "700")
            .style("color", "#2e7d32")
            .text(stat.value);
        
        statItem.append("div")
            .attr("class", "stat-label")
            .style("font-size", "0.8rem")
            .style("color", "#666")
            .style("margin-top", "4px")
            .text(stat.label);
        
        // Animar aparición de estadísticas
        setTimeout(() => {
            statItem
                .style("opacity", "1")
                .style("transform", "translateY(0)");
        }, 1000 + (i * 200));
    });
}

// Función auxiliar para formatear números
function formatearNumero(numero) {
    if (numero >= 1000) {
        return (numero / 1000).toFixed(1) + 'k';
    }
    return numero.toString();
}

// Función para hacer el dashboard responsive
function ajustarTamanoGraficos() {
    const cards = document.querySelectorAll('.card, .card-full');
    cards.forEach(card => {
        const svg = card.querySelector('svg');
        if (svg) {
            const containerWidth = card.clientWidth - 50; // padding
            svg.setAttribute('width', Math.min(containerWidth, 500));
        }
    });
}

// Escuchar cambios de tamaño de ventana
window.addEventListener('resize', ajustarTamanoGraficos);

// Mensaje de bienvenida en consola
console.log(`
🌿 EcoSoft Dashboard v2.0
🎓 Universidad Nacional de Educación (UNEMI) 2025
♻️ Proyecto de Clasificación Inteligente de Residuos
✅ Sistema cargado correctamente
`);