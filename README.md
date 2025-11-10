# 📦 Simulador de Planificación de Pedidos de Inventario (Contenedor y Base Contenedor)

Este proyecto es una aplicación web interactiva desarrollada en Python (Streamlit) diseñada para simular la evolución del stock de dos consumibles (`Contenedor` y `Base Contenedor`) a lo largo de 28 días (4 semanas). Además, calcula el **día óptimo de pedido** a largo plazo para evitar quiebres de stock, basándose en el stock inicial, el plazo de entrega y un patrón de consumo semanal.

## ✨ Características Principales

* **Doble Consumible:** Simula y rastrea de forma independiente los niveles de stock de dos artículos con diferentes parámetros.
* **Planificación a Largo Plazo:** Proyecta consumos para determinar la fecha concreta y óptima del próximo pedido necesario.
* **Horizonte de 28 Días:** Simulación detallada de entradas y salidas de stock durante cuatro semanas.
* **Interfaz Web (Streamlit):** Interfaz gráfica amigable para introducir la fecha de inicio, stock inicial y consumos diarios de manera sencilla.
* **Visualización:** Genera una gráfica `matplotlib` que ilustra la evolución del stock y señala los puntos de pedido planificados.

## 🛠️ Tecnología

* **Lenguaje:** Python (3.x)
* **Framework Web:** Streamlit
* **Análisis y Gráficos:** NumPy y Matplotlib
* **Gestión de Fechas:** Módulo `datetime`

## 🚀 Instalación y Ejecución

Sigue estos pasos para tener la aplicación web ejecutándose en tu máquina local.

### Requisitos

Necesitas tener Python 3.x instalado.

#### 1. Clonar el Repositorio

Abre tu terminal y clona el proyecto de GitHub:

#### 2. Crear y Activar un Entorno Virtual (Recomendado)
Es una buena práctica crear un entorno aislado para evitar conflictos de librerías:

#### 3. Instalar las Dependencias
Instala todas las librerías necesarias (Streamlit, Matplotlib, NumPy):

#### 4. Ejecutar la Aplicación Web
Una vez que las dependencias estén instaladas, ejecuta el script principal (app.py) usando Streamlit:

## ⚙️ Parámetros del Modelo
Los siguientes parámetros están definidos en el código (aunque el stock y el consumo son interactivos):

Consumible,Cantidad de Pedido (Q),Plazo de Entrega (Lead Time),Consumo Semanal Previsto
Contenedor,288 unidades,16 días,Aprox. 250 unidades
Base Contenedor,1000 unidades,16 días,Aprox. 500 unidades

## 📝 Uso
Configuración Inicial: Usa la barra lateral para introducir la fecha de inicio, el stock real actual de ambos consumibles.

* Programación de Consumos: En la barra lateral expandible, introduce el patrón de consumo diario (Lunes a Domingo). Este patrón se repetirá para la simulación de 28 días.

* Resultados: La sección principal de la aplicación mostrará:

  -  La Planificación Óptima de Pedidos (fecha concreta) para evitar futuros quiebres de stock.

  -  Una gráfica con la evolución proyectada del stock y la marcación de los puntos de pedido.
