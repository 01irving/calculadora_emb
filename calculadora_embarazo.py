import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(
    page_title="Calculadora Nutricional para Embarazo",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Funciones de cálculo
def calcular_imc(peso, talla):
    return peso / (talla ** 2)

def calcular_peso_esperado(imc_previo, peso_pregestacional, semanas):
    if imc_previo < 18.5:
        return peso_pregestacional + (0.322 * semanas)
    elif imc_previo >= 18.5 and imc_previo < 25:
        return peso_pregestacional + (0.267 * semanas)
    elif imc_previo >= 25 and imc_previo < 30:
        return peso_pregestacional + (0.237 * semanas)
    else:
        return peso_pregestacional + (0.183 * semanas)

def calcular_ree_no_embarazo(peso_pregestacional, edad, naf):
    if edad >= 18 and edad <= 30:
        ger = (14.818 * peso_pregestacional) + 486.6
    elif edad > 30 and edad <= 50:
        ger = (8.126 * peso_pregestacional) + 845.6
    else:
        ger = (65.3 * peso_pregestacional) - (0.454 * (peso_pregestacional ** 2)) + 263.4

    if edad >= 18:
        return ger * naf
    else:
        deposito_energia = calcular_deposito_energia(edad)
        return ger + deposito_energia

def calcular_deposito_energia(edad):
    depositos = {
        (12, 13): 26,
        (13, 14): 24,
        (14, 15): 19,
        (15, 16): 12,
        (16, 17): 5,
        (17, 18): 0
    }
    
    for (min_edad, max_edad), valor in depositos.items():
        if edad >= min_edad and edad < max_edad:
            return valor
    return None

def calcular_costo_energetico(trimestre_inicio, trimestre_gestacion):
    costos = {
        1: {1: 85, 2: 285, 3: 475},
        2: {2: 360, 3: 475}
    }
    return costos.get(trimestre_inicio, {}).get(trimestre_gestacion)

def calcular_get(peso_pregestacional, edad, naf):
    ree_no_embarazo = calcular_ree_no_embarazo(peso_pregestacional, edad, naf)
    
    if edad < 18:
        deposito_energia = calcular_deposito_energia(edad)
        get_adolescente = ree_no_embarazo + deposito_energia
        return {'ree_no_embarazo': ree_no_embarazo, 'get_adolescente': get_adolescente}
    return {'ree_no_embarazo': ree_no_embarazo}

def calcular_ree_embarazo(ree_no_embarazo, trimestre_inicio, trimestre_gestacion):
    costo_energetico = calcular_costo_energetico(trimestre_inicio, trimestre_gestacion)
    ree_embarazo = ree_no_embarazo + costo_energetico
    return {'ree_embarazo': ree_embarazo, 'costo_energetico': costo_energetico}

# Interfaz de usuario
st.title("Calculadora Nutricional para Embarazo")

# Crear dos columnas
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Datos de la Paciente")
    
    peso_pregestacional = st.number_input("Peso Pregestacional (kg)", 
                                        min_value=30.0, max_value=200.0, value=60.0)
    
    talla = st.number_input("Talla (m)", 
                           min_value=1.0, max_value=2.5, value=1.65)
    
    edad = st.number_input("Edad (años)", 
                          min_value=12, max_value=50, value=25)
    
    semanas = st.number_input("Semanas de Gestación", 
                             min_value=1, max_value=42, value=20)
    
    trimestre_inicio = st.selectbox("Trimestre de Inicio del Control", 
                                   options=[1, 2], 
                                   format_func=lambda x: f"{x}° Trimestre")
    
    trimestre_actual = st.selectbox("Trimestre de Gestación Actual", 
                                   options=[1, 2, 3], 
                                   format_func=lambda x: f"{x}° Trimestre")
    
    # NAF simplificado
    naf = st.number_input("NAF (Nivel de Actividad Física)", 
                         min_value=1.0, 
                         max_value=2.5, 
                         value=1.5,
                         step=0.1)
    
    calcular = st.button("Calcular")

with col2:
    if calcular:
        st.subheader("Resultados")
        
        # Cálculos
        imc_previo = calcular_imc(peso_pregestacional, talla)
        peso_esperado = calcular_peso_esperado(imc_previo, peso_pregestacional, semanas)
        resultados_get = calcular_get(peso_pregestacional, edad, naf)
        
        # Mostrar resultados
        col_res1, col_res2 = st.columns(2)
        
        with col_res1:
            # IMC
            st.metric("IMC Pregestacional", f"{imc_previo:.2f} kg/m²")
            
            # Clasificación IMC
            if imc_previo < 18.5:
                estado = "Bajo peso"
                color = "🔴"
            elif imc_previo < 25:
                estado = "Normal"
                color = "🟢"
            elif imc_previo < 30:
                estado = "Sobrepeso"
                color = "🟡"
            else:
                estado = "Obesidad"
                color = "🔴"
            
            st.write(f"Clasificación: {color} {estado}")
            
            # Peso esperado
            st.metric("Peso Esperado", f"{peso_esperado:.2f} kg")
            st.write(f"Ganancia esperada: {peso_esperado - peso_pregestacional:.2f} kg")
        
        with col_res2:
            if edad < 18:
                costo_energetico = calcular_costo_energetico(trimestre_inicio, trimestre_actual)
                ree_embarazo = resultados_get['get_adolescente'] + costo_energetico
                
                st.metric("GET del Embarazo", f"{resultados_get['get_adolescente']:.0f} kcal/día")
                st.metric("Costo Energético", f"{costo_energetico:.0f} kcal/día")
                st.metric("REE del Embarazo", f"{ree_embarazo:.0f} kcal/día")
            else:
                resultados_ree_embarazo = calcular_ree_embarazo(
                    resultados_get['ree_no_embarazo'], 
                    trimestre_inicio, 
                    trimestre_actual
                )
                
                st.metric("GET del Embarazo", 
                         f"{resultados_get['ree_no_embarazo']:.0f} kcal/día")
                st.metric("Costo Energético", 
                         f"{resultados_ree_embarazo['costo_energetico']:.0f} kcal/día")
                st.metric("REE del Embarazo", 
                         f"{resultados_ree_embarazo['ree_embarazo']:.0f} kcal/día")
        
        # Gráfico de progresión de peso usando matplotlib en lugar de plotly
        st.subheader("Progresión de Peso Esperada")
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Datos para el gráfico
        semanas_totales = list(range(1, 43))
        pesos_esperados = [calcular_peso_esperado(imc_previo, peso_pregestacional, s) 
                          for s in semanas_totales]
        
        # Línea de progresión
        ax.plot(semanas_totales, pesos_esperados, label='Peso esperado')
        
        # Punto actual
        ax.scatter([semanas], [peso_esperado], color='red', s=100, label='Semana actual')
        
        # Configuración del gráfico
        ax.set_title('Progresión de Peso Durante el Embarazo')
        ax.set_xlabel('Semanas de Gestación')
        ax.set_ylabel('Peso (kg)')
        ax.grid(True)
        ax.legend()
        
        # Mostrar el gráfico
        st.pyplot(fig)

# Notas y referencias
st.markdown("""
---
**Notas:**
- Los cálculos se basan en las recomendaciones de la OMS y el IOM (Institute of Medicine)
- El GET (Gasto Energético Total) incluye el factor de actividad física
- El REE (Requerimiento Energético en Embarazo) incluye el costo energético del embarazo

**Referencias:**
- Institute of Medicine. Weight Gain During Pregnancy: Reexamining the Guidelines
- WHO/FAO/UNU. Human energy requirements
- De León Fraga, J. (Dir. Ed.), & Guerrero Aguilar, H. F. (Ed. Des.). (2012). Manual de fórmulas y tablas para la intervención nutriológica (2ª ed.). McGraw-Hill Interamericana Editores.
""")