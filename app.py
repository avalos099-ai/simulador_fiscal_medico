import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración inicial del portal / app
st.set_page_config(
    page_title="Simulador Fiscal para Médicos | TaxMed",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para apariencia médica y financiera profesional
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .tax-badge {
        background-color: #E0F2FE;
        color: #0369A1;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)



def calcular_isr_resico(ingreso_bruto):
    """
    Calcula el ISR mensual para RESICO Personas Físicas
    Tablas vigentes LISR (RESICO)
    """
    if ingreso_bruto <= 0:
        return 0.0, 0.0
    
    if ingreso_bruto <= 25000:
        tasa = 0.0100
    elif ingreso_bruto <= 50000:
        tasa = 0.0110
    elif ingreso_bruto <= 83333.33:
        tasa = 0.0150
    elif ingreso_bruto <= 166666.67:
        tasa = 0.0200
    elif ingreso_bruto <= 2916666.67:
        tasa = 0.0250
    else:
        # Excede el límite de RESICO (3.5 MDP anuales / ~291,666 mensual)
        tasa = 0.0250 

    isr_causado = ingreso_bruto * tasa
    return isr_causado, tasa


def calcular_isr_actividad_profesional(utilidad_gravable):
    """
    Calcula el ISR mensual bajo Actividad Profesional (Honorarios)
    Usando la tarifa mensual de ISR con límite inferior, cuota fija y % excedente
    """
    if utilidad_gravable <= 0:
        return 0.0

    # Tabla mensual aproximada de ISR
    tabla_isr = [
        {"lim_inf": 0.01, "lim_sup": 746.04, "cuota_fija": 0.00, "porcentaje": 0.0192},
        {"lim_inf": 746.05, "lim_sup": 6332.05, "cuota_fija": 14.32, "porcentaje": 0.0640},
        {"lim_inf": 6332.06, "lim_sup": 11128.01, "cuota_fija": 371.83, "porcentaje": 0.1088},
        {"lim_inf": 11128.02, "lim_sup": 12935.82, "cuota_fija": 893.63, "porcentaje": 0.1600},
        {"lim_inf": 12935.83, "lim_sup": 15487.71, "cuota_fija": 1182.88, "porcentaje": 0.1792},
        {"lim_inf": 15487.72, "lim_sup": 31236.49, "cuota_fija": 1640.18, "porcentaje": 0.2136},
        {"lim_inf": 31236.50, "lim_sup": 49233.00, "cuota_fija": 5004.12, "porcentaje": 0.2352},
        {"lim_inf": 49233.01, "lim_sup": 93993.90, "cuota_fija": 9236.89, "porcentaje": 0.3000},
        {"lim_inf": 93993.91, "lim_sup": 125325.20, "cuota_fija": 22665.17, "porcentaje": 0.3200},
        {"lim_inf": 125325.21, "lim_sup": 375975.61, "cuota_fija": 32691.18, "porcentaje": 0.3400},
        {"lim_inf": 375975.62, "lim_sup": float('inf'), "cuota_fija": 117912.32, "porcentaje": 0.3500},
    ]

    for tramo in tabla_isr:
        if tramo["lim_inf"] <= utilidad_gravable <= tramo["lim_sup"]:
            excedente = utilidad_gravable - tramo["lim_inf"]
            impuesto_marginal = excedente * tramo["porcentaje"]
            isr_total = tramo["cuota_fija"] + impuesto_marginal
            return isr_total

    return 0.0



st.sidebar.image("https://img.icons8.com/color/96/stethoscope.png", width=70)
st.sidebar.title("🩺 Perfil Médico")
st.sidebar.markdown("---")

nombre_medico = st.sidebar.text_input("Nombre / Doctor(a):", value="Dr. Alejandro Silva")
especialidad = st.sidebar.selectbox(
    "Especialidad / Ámbito:",
    ["Medicina General", "Pediatría", "Cirugía General", "Odontología / Ortodoncia", "Dermatología", "Ginecología", "Otro"]
)

regimen_actual = st.sidebar.radio(
    "Régimen Fiscal Actual:",
    ["RESICO (Régimen Simplificado)", "Actividad Profesional (Honorarios)"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("💰 Ingresos Mensuales")

ingreso_pf = st.sidebar.number_input(
    "Honorarios cobrados a Personas Físicas ($):",
    min_value=0.0, value=65000.0, step=5000.0,
    help="Consultas directas a pacientes particulares."
)

ingreso_pm = st.sidebar.number_input(
    "Honorarios cobrados a Personas Morales ($):",
    min_value=0.0, value=35000.0, step=5000.0,
    help="Facturado a Hospitales, Aseguradoras, Clínicas o Empresas."
)

ingreso_total = ingreso_pf + ingreso_pm

st.sidebar.markdown("---")
st.sidebar.subheader("📉 Gastos / Deducciones")

gastos_autorizados = st.sidebar.number_input(
    "Deducciones de Operación ($):",
    min_value=0.0, value=28000.0, step=2000.0,
    help="Renta de consultorio, insumos médicos, mantenimiento, asistente, etc."
)



st.markdown('<div class="main-header">Simulador & Calculadora Fiscal para Médicos ⚕️</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Plataforma interactiva para la optimización contable y proyección de ISR de profesionales de la salud.</div>', unsafe_allow_html=True)

# Pestañas de la aplicación
tab_calculo, tab_deducciones, tab_recomendaciones = st.tabs([
    "🧮 Cálculo & Comparativa de ISR",
    "📋 Checklist de Deducciones Médicas",
    "💡 Marco Legal & Recomendaciones"
])



with tab_calculo:
    st.info("ℹ️ **Nota Fiscal Clave:** Los servicios profesionales de medicina prestados por personas físicas están **EXENTOS de IVA** de acuerdo con el **Artículo 15, Fracción XIV de la Ley del IVA** (siempre que requieran título de médico).")

    # Cálculos en tiempo real
    
    # 1. RETENCIONES POR PERSONA MORAL
    if "RESICO" in regimen_actual:
        retencion_pm_rate = 0.0125  # 1.25% en RESICO
    else:
        retencion_pm_rate = 0.1000  # 10.0% en Actividad Profesional
        
    retencion_efectuada = ingreso_pm * retencion_pm_rate

    # 2. CALCULOS RESICO
    isr_resico_causado, tasa_resico = calcular_isr_resico(ingreso_total)
    retencion_resico = ingreso_pm * 0.0125
    isr_resico_a_pagar = max(0.0, isr_resico_causado - retencion_resico)
    neto_resico = ingreso_total - isr_resico_a_pagar

    # 3. CALCULOS ACTIVIDAD PROFESIONAL
    utilidad_act_prof = max(0.0, ingreso_total - gastos_autorizados)
    isr_act_prof_causado = calcular_isr_actividad_profesional(utilidad_act_prof)
    retencion_act_prof = ingreso_pm * 0.10
    isr_act_prof_a_pagar = max(0.0, isr_act_prof_causado - retencion_act_prof)
    neto_act_prof = ingreso_total - gastos_autorizados - isr_act_prof_a_pagar

    # Resumen Ejecutivo Superior
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Ingreso Bruto Total", f"${ingreso_total:,.2f}")
    with col2:
        st.metric("Retención ISR (PM)", f"${retencion_efectuada:,.2f}", help="ISR retenido por clínicas o aseguradoras")
    with col3:
        if "RESICO" in regimen_actual:
            st.metric("ISR a Pagar (RESICO)", f"${isr_resico_a_pagar:,.2f}", delta=f"Tasa: {tasa_resico*100:.2f}%")
        else:
            st.metric("ISR a Pagar (Honorarios)", f"${isr_act_prof_a_pagar:,.2f}", delta=f"Utilidad: ${utilidad_act_prof:,.0f}")
    with col4:
        st.metric("Ingreso Disponible Neto", f"${(neto_resico if 'RESICO' in regimen_actual else neto_act_prof):,.2f}")

    st.markdown("---")

    st.subheader("⚖️ Comparativa Estratégica: RESICO vs. Actividad Profesional")
    st.write("Analice qué régimen fiscal le conviene más según su nivel de ingresos y deducciones operativas:")

    comp_col1, comp_col2 = st.columns([1, 1])

    with comp_col1:
        # Tabla comparativa
        df_comp = pd.DataFrame({
            "Concepto": [
                "Ingreso Bruto Total",
                "Deducciones Permitidas",
                "Base Gravable ISR",
                "ISR Causado (Teórico)",
                "Retención PM (Abono)",
                "🔴 ISR Neto a Pagar en Banco",
                "💚 Flujo Disponible Final"
            ],
            "RESICO ⚡": [
                f"${ingreso_total:,.2f}",
                "No Aplica para ISR",
                f"${ingreso_total:,.2f}",
                f"${isr_resico_causado:,.2f} ({tasa_resico*100:.1f}%)",
                f"${retencion_resico:,.2f} (1.25%)",
                f"${isr_resico_a_pagar:,.2f}",
                f"${(ingreso_total - isr_resico_a_pagar - gastos_autorizados):,.2f}"
            ],
            "Actividad Profesional 📂": [
                f"${ingreso_total:,.2f}",
                f"${gastos_autorizados:,.2f}",
                f"${utilidad_act_prof:,.2f}",
                f"${isr_act_prof_causado:,.2f}",
                f"${retencion_act_prof:,.2f} (10%)",
                f"${isr_act_prof_a_pagar:,.2f}",
                f"${neto_act_prof:,.2f}"
            ]
        })
        st.dataframe(df_comp, hide_index=True, use_container_width=True)

        # Recomendación automática
        diferencia_pago = abs(isr_resico_a_pagar - isr_act_prof_a_pagar)
        if isr_resico_a_pagar < isr_act_prof_a_pagar:
            st.success(f"💡 **Diagnóstico Fiscal:** **RESICO** le genera un ahorro estimado de **${diferencia_pago:,.2f} MXN al mes** en pago directo de ISR frente al régimen tradicional de Honorarios.")
        else:
            st.warning(f"💡 **Diagnóstico Fiscal:** El régimen de **Actividad Profesional** resulta más ventajoso por su alto volumen de deducciones operativas (Ahorro de **${diferencia_pago:,.2f} MXN**).")

    with comp_col2:
        # Gráfica interactiva Plotly
        fig = go.Figure(data=[
            go.Bar(name='ISR Causado', x=['RESICO', 'Act. Profesional'], y=[isr_resico_causado, isr_act_prof_causado], marker_color='#EF4444'),
            go.Bar(name='Retención por PM', x=['RESICO', 'Act. Profesional'], y=[retencion_resico, retencion_act_prof], marker_color='#F59E0B'),
            go.Bar(name='ISR Final a Pagar', x=['RESICO', 'Act. Profesional'], y=[isr_resico_a_pagar, isr_act_prof_a_pagar], marker_color='#10B981')
        ])
        fig.update_layout(
            title='Desglose Comparativo de Impuestos (Mensual)',
            barmode='group',
            height=450,
            margin=dict(l=20, r=20, t=100, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)



with tab_deducciones:
    st.subheader("🩺 Deducciones Autorizadas Específicas para Médicos")
    st.write("Si tributas en **Actividad Profesional**, estos gastos son 100% deducibles para reducir la base imponible del ISR (deben ser pagados con medios electrónicos y contar con CFDI 4.0):")

    col_d1, col_d2 = st.columns(2)

    with col_d1:
        st.markdown("### 🏬 Infraestructura & Operación")
        st.checkbox("Renta de Consultorio Médico / Cubículo", value=True)
        st.checkbox("Servicios del Consultorio (Luz, Agua, Internet, Teléfono)", value=True)
        st.checkbox("Sueldo de Asistente, Enfermera o Recepcionista (Nómina)", value=False)
        st.checkbox("Honorarios de Contador / Mantenimiento de Software Médico", value=True)
        st.checkbox("Mantenimiento y Calibración de Equipo Médico", value=False)

        st.markdown("### 💉 Insumos & Materiales")
        st.checkbox("Material Curativo, Guantes, Jeringas y Consumibles", value=True)
        st.checkbox("Medicamentos comprados para aplicación en Consultorio", value=False)
        st.checkbox("Servicios de Laboratorio o Radiología Subcontratados", value=False)

    with col_d2:
        st.markdown("### 📚 Crecimiento & Protección Legal")
        st.checkbox("Seguro de Responsabilidad Civil Professional (Malpraxis)", value=True)
        st.checkbox("Cuotas a Colegios Médicos y Certificaciones de Consejo", value=True)
        st.checkbox("Inscripción a Congresos Médicos, Cursos y Posgrados", value=True)
        st.checkbox("Suscripción a Revistas Científicas / Expediente Clínico Digital", value=True)

        st.markdown("### 💻 Equipo & Mobiliario (Depreciación/Inversión)")
        st.checkbox("Computadora, Tableta y Celular de Uso Profesional", value=True)
        st.checkbox("Mobiliario de Consultorio (Mesa de exploración, Báscula, etc.)", value=False)
        st.checkbox("Equipo Diagnóstico (Escáner, Ultrasonido, Electrocardiógrafo)", value=False)

    st.markdown("---")
    st.caption("🚨 *Nota:* En RESICO no se deducen gastos para el cálculo mensual de ISR (ya que la tasa es muy baja, del 1% al 2.5%), pero conservar las facturas de gastos sigue siendo obligatorio para efectos contables y de IVA si realiza actividades no exentas.")



with tab_recomendaciones:
    st.subheader("📌 Puntos Fiscales Críticos para Profesionales de la Salud")

    exp_iva = st.expander("1. ¿Por qué el servicio médico no cobra IVA?", expanded=True)
    exp_iva.write("""
    El **Artículo 15, fracción XIV de la Ley del IVA** establece que no se pagará el impuesto por la prestación de servicios profesionales de medicina, siempre que:
    *   Sean prestados por **Personas Físicas** individualmente o a través de Sociedades Civiles.
    *   Se requiera **Título de Médico** conforme a las leyes aplicables.
    *   *Excepción:* Análisis clínicos, estudios radiológicos o venta de medicamentos/suplementos sí pueden llevar IVA al 16% o 0% según el caso.
    """)

    exp_resico = st.expander("2. ¿Cuándo le conviene al médico cambiarse a RESICO?")
    exp_resico.write("""
    *   Cuando sus ingresos anuales **no superen los $3.5 MDP**.
    *   Cuando sus **gastos operativos sean bajos** en relación con sus cobros.
    *   Cuando facture principalmente a **Personas Morales** (Aseguradoras, Hospitales), ya que solo le retendrán el **1.25% de ISR** (en lugar del 10%).
    *   *Restricción:* No puede estar en RESICO si percibe ingresos por asimilados a salarios en ciertos esquemas o dividendos de empresas socio.
    """)

    exp_pacientes = st.expander("3. Facturación a Pacientes Particulares (Público en General)")
    exp_pacientes.write("""
    *   Es obligatorio emitir **CFDI Global** semanal o mensual por los ingresos de pacientes que no solicitaron factura individual.
    *   Para pacientes que solicitan factura individual para sus **Deducciones Personales** anuales, la factura debe indicar la forma de pago (Tarjeta de Crédito/Débito, Transferencia, Cheque). **Si se paga en efectivo, el paciente no podrá deducirla.**
    """)

    st.markdown("---")
    st.markdown("### 📄 Descargar Reporte de Proyección")
    st.button("📥 Exportar Simulación en PDF (Demo para cliente)", type="primary")

st.markdown("---")
st.caption("👨‍💻 *Prototipo desarrollado para demostración en consultoría contable y fiscal para médicos en México.*")