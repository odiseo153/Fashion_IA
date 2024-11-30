$(document).ready(function () {
  // Diccionario de características físicas
  const caracteristicas_fisicas = {
      "Género": ['hombre', 'mujer'],
      "Tono de piel": ['negra', 'blanca', 'morena', 'moreno', 'clara', 'oscura', 'prieto'],
      "Contextura física": ['corpulento', 'delgado', 'atlético', 'robusto', 'corpulenta', 'delgada', 'atlética', 'robusta', 'normal', 'atlético', 'atlética', 'gorda', 'esbelta', 'esbelto'],
      "Color de ojos": ['verde', 'azules', 'marrones', 'grises', 'avellana', 'amarillo', 'negro', 'gris', 'marron', 'azul', 'rojo', 'verdes'],
      "Estatura": ['alto', 'medio', 'alta', 'mediano', 'baja', 'media'],
      "Personalidad": ['seguro', 'confiado', 'audaz', 'tranquilo', 'relajado', 'introvertido', 'extrovertido', 'sociable', 'enérgico', 'segura', 'confiada', 'audaz', 'tranquila', 'relajada', 'introvertida', 'extrovertida', 'energica', 'casual', 'práctico', 'deportivo', 'deportiva', 'sofisticado', 'sofisticada', 'creativa', 'tranquila', 'clásico', 'clasica', 'aventurero', 'elegante', 'aventurera', 'tranquilo.tranquila'],
      "Evento": ['reunion', 'entrevista', 'cenas formales', 'cenas de negocios', 'fiestas', 'conferencias', 'presentaciones', 'salidas', 'citas', 'misa', 'ceremonia', 'informales', 'casual', 'playa', 'casa', 'vacaciones', 'actividad deportiva', 'paseos', 'cine', 'reuniones casuales', 'salida nocturna', 'evento fomal', 'reunion al aire libre', 'ocasion especial', 'reuniones', 'evento de verano', 'trabajo', 'paseo', 'ocasion formal', 'boda', 'cena formal', 'eventos de gala']
  };

  let totalPaginas = 0; // Declarar totalPaginas en el ámbito superior
  let paginaActual = 1; // Declarar paginaActual en el ámbito superior

  // Inicializar funciones
  inicializarEventos();

  function inicializarEventos() {
      $("#name").on("input", manejarInputNombre);
      $("#characteristics-list").on("click", mostrarSugerencias);
      $("#toggle-suggestions").on("click", manejarToggleSuggestions);
      document.getElementById('close-modal').addEventListener('click', cerrarModal);
  }

  // Función para verificar cuántas características físicas están presentes en la descripción
  function contarCaracteristicas(text) {
      let count = 0;

      Object.values(caracteristicas_fisicas).forEach((suggestions) => {
          suggestions.forEach((item) => {
              const regex = new RegExp(`\\b${item}\\b`, "i"); // Buscar coincidencias exactas, no parciales
              if (regex.test(text)) {
                  count++;
              }
          });
      });

      return count;
  }

  function manejarInputNombre() {
      const campo = $(this).val();
      const caracteristicasDetectadas = contarCaracteristicas(campo);

      // Habilitar el botón si hay al menos 2 características detectadas
      $("#toggle-suggestions").prop("disabled", caracteristicasDetectadas < 2);
  }

  function mostrarSugerencias() {
      $("#suggestions").prop("hidden", false);
  }

  function manejarToggleSuggestions(event) {
      event.preventDefault();

      const nameInput = $("#name").val();
      const productContainer = $("#recommended-images"); // Contenedor para los productos
      const paginacionContainer = $("#paginacion"); // Contenedor para la paginación
      productContainer.empty(); // Limpiar productos previos
      paginacionContainer.empty(); // Limpiar la paginación previa

      $("#spinner").removeClass("hidden"); // Mostrar spinner de carga
      $(".container").addClass("opacity-50"); // Reducir opacidad mientras carga

      // Simulación de petición AJAX
      $.ajax({
          url: "/predict", // Cambia esto a tu endpoint real
          method: "POST",
          contentType: "application/json",
          data: JSON.stringify({ texto: nameInput }),
          success: function (data) {
            console.log(data);
              manejarDatosProductos(data, productContainer, paginacionContainer);
          },
          error: function (error) {
              console.error("Error:", error);
          },
          complete: function () {
              $("#spinner").addClass("hidden"); // Ocultar spinner de carga
              $(".container").removeClass("opacity-50"); // Restaurar opacidad
          },
      });
  }

  function manejarDatosProductos(data, productContainer, paginacionContainer) {
      if (data.products && data.products.length > 0) {
          const productosPorPagina = 8; // Número de productos por página
          totalPaginas = Math.ceil(data.products.length / productosPorPagina); // Calcular total de páginas
          
          // Mostrar la primera página de productos
          mostrarProductos(data, productContainer, productosPorPagina, paginaActual);
          // Generar paginación
          generarPaginacion(data.products.length, paginacionContainer, productosPorPagina);
          $("#sugerencias").removeClass("hidden"); // Mostrar las sugerencias
      }
  }

  function mostrarProductos(data, productContainer, productosPorPagina, pagina) {
      const indexUltimoProducto = pagina * productosPorPagina;
      const indexPrimerProducto = indexUltimoProducto - productosPorPagina;
      const productosActuales = data.products.slice(indexPrimerProducto, indexUltimoProducto);
      
      productContainer.empty(); // Limpiar productos previos
      
      productosActuales.forEach(function (producto) {
          const productElement = crearElementoProducto(producto);
          productContainer.append(productElement);
      });
      
      // Asegurarse de que el contenedor crezca dinámicamente
      productContainer.css('display', 'grid');
  }

  function generarPaginacion(totalProductos, paginacionContainer, productosPorPagina) {
      paginacionContainer.empty(); // Limpiar paginación previa

      const totalPaginas = Math.ceil(totalProductos / productosPorPagina);
      const maxBotones = 5; // Número máximo de botones de paginación a mostrar
      let inicioPagina = Math.max(1, paginaActual - Math.floor(maxBotones / 2));
      let finPagina = Math.min(totalPaginas, inicioPagina + maxBotones - 1);

      if (finPagina - inicioPagina + 1 < maxBotones) {
          inicioPagina = Math.max(1, finPagina - maxBotones + 1);
      }

      for (let i = inicioPagina; i <= finPagina; i++) {
          const pageItem = crearElementoPagina(i);
          paginacionContainer.append(pageItem);
      }

      // Añadir botones "anterior" y "siguiente" si es necesario
      if (paginaActual > 1) {
          const prevButton = crearBotonAnterior();
          paginacionContainer.prepend(prevButton);
      }

      if (paginaActual < totalPaginas) {
          const nextButton = crearBotonSiguiente();
          paginacionContainer.append(nextButton);
      }
  }
  function toggleModal() {
    const modal = document.getElementById('productModal');
    modal.classList.toggle('hidden');
  }
  
  function openProductModal(product) {
    // Actualiza los datos del modal con la información del producto
    document.getElementById('modalProductImage').src = product.product_photo;
    document.getElementById('modalProductTitle').textContent = product.product_title;
    document.getElementById('modalProductPrice').textContent = product.product_price;
    document.getElementById('modalProductDelivery').textContent = product.delivery;
    document.getElementById('modalProductAsin').textContent = product.asin;
    document.getElementById('modalProductRating').textContent = product.product_star_rating;
    document.getElementById('modalProductNumRatings').textContent = product.product_num_ratings;
    document.getElementById('modalSalesVolume').textContent = product.sales_volume;
    document.getElementById('modalAmazonPrime').textContent = product.is_prime ? "Prime" : "No Prime";
    document.getElementById('modalProductUrl').href = product.product_url;
  
    // Muestra el modal
    toggleModal();
  }
  
  function crearElementoProducto(producto) {
    return `
      <div class="producto flex flex-col border border-gray-300 rounded-lg shadow-lg p-4 hover:shadow-xl transform hover:-translate-y-1 transition-all cursor-pointer" onclick="openProductModal(${JSON.stringify(producto).replace(/"/g, '&quot;')})">
        <!-- Imagen del producto -->
        <img src="${producto.product_photo}" alt="Producto" class="w-full h-48 object-cover mb-4 rounded-lg">
  
        <!-- Contenido del producto -->
        <div class="flex-grow">
          <h2 class="text-lg font-semibold text-white line-clamp-2 mb-2">${producto.product_title}</h2>
          <p class="text-2xl font-bold text-blue-600 mt-1">${producto.product_price}</p>
        </div>
  
        <!-- Calificación -->
        <div class="mt-4 flex items-center text-sm text-gray-600">
          <span class="text-yellow-500 mr-1">★</span> 
          ${producto.product_star_rating} 
          <span class="ml-2">(${producto.product_num_ratings} valoraciones)</span>
        </div>
  
        <!-- Botón de acción -->
        <div class="mt-4">
          <a href="${producto.product_url}" target="_blank" 
            class="block w-full px-4 py-2 text-center bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-semibold transition-colors">
            Ver en Amazon
          </a>
        </div>
      </div>
    `;
  }
  
  

  function crearElementoPagina(i) {
      return `<button class="p-2 ${paginaActual === i ? 'font-bold' : ''}" data-pagina="${i}">${i}</button>`;
  }

  function crearBotonAnterior() {
      return `<button class="p-2" id="prev-button">Anterior</button>`;
  }

  function crearBotonSiguiente() {
      return `<button class="p-2" id="next-button">Siguiente</button>`;
  }

  function cerrarModal() {
      $("#modal").removeClass("hidden");
  }

  // Manejar eventos de paginación
  $(document).on('click', '#paginacion button', function () {
      const nuevaPagina = $(this).data("pagina");
      if (nuevaPagina) {
          paginaActual = nuevaPagina;
          mostrarProductos(data, productContainer, productosPorPagina, paginaActual);
          generarPaginacion(data.products.length, paginacionContainer, productosPorPagina);
      } else if ($(this).is("#prev-button")) {
          if (paginaActual > 1) {
              paginaActual--;
              mostrarProductos(data, productContainer, productosPorPagina, paginaActual);
              generarPaginacion(data.products.length, paginacionContainer, productosPorPagina);
          }
      } else if ($(this).is("#next-button")) {
          if (paginaActual < totalPaginas) {
              paginaActual++;
              mostrarProductos(data, productContainer, productosPorPagina, paginaActual);
              generarPaginacion(data.products.length, paginacionContainer, productosPorPagina);
          }
      }
  });
});
