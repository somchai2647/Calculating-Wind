import streamlit as st
import pandas as pd
import numpy as np
from scipy import interpolate
from PIL import Image
import altair as alt

st.write(r'# การคำนวณแรงลมสำหรับอาคารสูง')
st.write(r'## ตามมาตรฐาน มยผ.1311-50 ด้วยวิธีอย่างง่าย')

st.write(r'### มิติอาคาร')
col1,col2 = st.columns([0.3,0.7])
with col1:
    Floor = st.number_input(label='จำนวนชั้น', min_value=1, max_value=24, value=3, step=1)
    Widthx = st.number_input(label=r'$ความกว้างตามแนวแกน \quad x$', min_value=0.0, value=3.0, step=0.1) 
    Widthy = st.number_input(label=r'$ความกว้างตามแนวแกน \quad y$', min_value=0.0, value=3.0, step=0.1) 
    Ds = min(Widthx,Widthy)
    st.write(r'$D_s = %.2f \mathrm{~m}$'%(Ds))
with col2:
    col1x,col2x = st.columns(2)
    with col1x:
        Floors = pd.DataFrame({'Floors':[],})
        Wx = 0
        Wy = 0
        Floor_list = []
        H = 0
        for i in range(Floor):
            Heigh = st.number_input(label=r'$ความสูงของชั้นที่ \quad %i$'%(i+1), min_value=0.0, value=3.0, step=0.1,key=f"floor_{i}")
            H += Heigh
            with col2x:
                if H > 80:
                    st.warning((r"$ความสูงของอาคารเกิน \quad 80 \quad m!$"))
                    break
                Floor_list.append(H)
                Floors.loc[i+1] = i+1
                Wx = Wx + (H*Widthx)
                Sum_Wx = 3*Wx/H
                if Sum_Wx < H:
                    st.markdown('')
                    st.warning((r"$3 \quad เท่าของความกสว้างน้อยกว่าความสูง!$"))
                    break
                Wy = Wy + (H*Widthy)
                Sum_Wy = 3*Wy/H
                if Sum_Wy < H:
                    st.markdown('')
                    st.warning((r"$3 \quad เท่าของความกสว้างน้อยกว่าความสูง!$"))
                    break
                if i == Floor - 1 and H/Ds < 1:
                    st.markdown('')
                    st.warning((r"$H/D_s \quad น้อยกกว่า \quad  1!$")) 
                    break 
                        
df_important = pd.DataFrame({
    'ประเภทความสำคัญ': ['น้อย', 'ปกติ', 'มาก', 'สูงมาก'],
    'สภาวะจำกัดด้านกำลัง': [0.8, 1.0, 1.15, 1.15],
    'สภาวะจำกัดด้านการใช้งาน': [0.75, 0.75, 0.75, 0.75],
})

st.write(r'### ค่าประกอบความสำคัญของแรงลม, $I$')
col1,col2,col3 = st.columns(3)
with col1:
    important_type = st.selectbox(label='ประเภทความสำคัญ', options=df_important['ประเภทความสำคัญ'])

with col2:
    cal_type = st.selectbox(label='ประเภทการออกแบบ', options=['สภาวะจำกัดด้านกำลัง', 'สภาวะจำกัดด้านการใช้งาน'])

with col3:
    Iw = float(df_important.loc[df_important['ประเภทความสำคัญ'] == important_type, cal_type])
    st.markdown('')
    st.markdown('')
    st.write(r'$I = %.2f$'%(Iw))

df_wind_speed = pd.DataFrame({
    'กลุ่ม': ['1', '2', '3', '4A', '4B'],
    'V50 [m/s]': [25, 27, 29, 25, 25],
    'T_F': [1.0, 1.0, 1.0, 1.2, 1.08],
})

st.write(r'### ความเร็วลมอ้างอิง, $\overline{V}$')
col1,col2 = st.columns(2)
with col1:
    area_group = st.selectbox(label='กลุ่มพื้นที่', options=df_wind_speed['กลุ่ม'])
    V50 = df_wind_speed.loc[df_wind_speed['กลุ่ม'] == area_group, 'V50 [m/s]']
    T_F = df_wind_speed.loc[df_wind_speed['กลุ่ม'] == area_group, 'T_F']
    if cal_type == 'สภาวะจำกัดด้านกำลัง':     
        V = float(V50*T_F)
        col1x,col2x,col3x = st.columns(3)
        with col1x:
            st.write(r'$V_{50} = %.2f \mathrm{~m/s}$'%(V50))
        with col2x:
            st.write(r'$T_F = %.2f$'%(T_F))
        with col3x:
            st.write(r'$\overline{V} = %.2f \mathrm{~m/s}$'%(V))
    else:
        V = float(V50)
        col1x,col2x = st.columns(2)
        with col1x:
            st.write(r'$V_{50} = %.2f \mathrm{~m/s}$'%(V50))
        with col2x:
            st.write(r'$\overline{V} = %.2f \mathrm{~m/s}$'%(V))

with st.expander("See table"):
    col1,col2 = st.columns(2)
    with col1:
        st.dataframe(df_wind_speed, hide_index=True, use_container_width=True)

st.write(r'### หน่วยแรงลมอ้างอิง, $q$')
col1, col2 = st.columns(2)
with col1:
    rho = 1.25
    g = 9.81
    q = 0.5*rho*(V**2)/g
    st.write(r'$q = %.2f \mathrm{~kg/m^2}$'%(q))

st.write(r'### ค่าประกอบเนื่องจากการกระโชกของลม, $C_g$')
col1, col2 = st.columns(2)
with col1:
    Cg = float(2)
    st.write(r'$Cg = %.2f \mathrm{~m}$'%(Cg))

st.write(r'### ค่าประกอบเนื่องจากสภาพภูมิประเทศ, $C_e$')
col1, col2 = st.columns(2)
with col1:
    land_type = st.selectbox(label='สภาพภูมิประเทศ', options=['แบบ A', 'แบบ B'])
    Ceup_list = [] 
    if land_type == 'แบบ A':
        for i in Floor_list:
            Ceup = max((i/10)**0.2,0.9)
            Ceup_list.append(Ceup)
        Cedown = max((H/10/2)**0.2,0.9)
    else:
        for i in Floor_list:    
            Ceup = max(0.7*(i/12)**0.3,0.7)
            Ceup_list.append(Ceup)
        Cedown = max(0.7*(H/12)**0.3,0.7)
    Ce_list = pd.DataFrame(Floors)
    Ce_list['Ce,up'] = Ceup_list
    Ce_list['Ce,up'] = Ce_list['Ce,up'].round(2)
    Ce_list['Ce,down'] = Cedown
    Ce_list['Ce,down'] = Ce_list['Ce,down'].round(2)  
    st.dataframe(Ce_list, hide_index=True, use_container_width=True)  

df_Cpi = pd.DataFrame({
    'ประเภท': ['อาคารที่ปราศจากช่องเปิดขนาดใหญ่', 'อาคารที่มีการรั่วซึม', 'อาคารที่มีช่องเปิดขนาดใหญ่'],
    'Cpi_minus': [-0.15,-0.45,-0.7],
    'Cpi_plus': [0.0,0.3,0.7],
})

st.write(r'### ค่าสัมประสิทธิ์ของหน่วยแรงลมภายใน, $C_{pi}$')
col1,col2 = st.columns(2)
with col1:
    Type_Building = st.selectbox(label='ประเภทอาคาร', options=df_Cpi['ประเภท'])
    col1x,col2x = st.columns(2)
    with col1x:
        Cpi_minus = float(df_Cpi.loc[df_Cpi['ประเภท'] == Type_Building, 'Cpi_minus'])
        st.write(r'$C_{pi}⁻ = %.2f$'%(Cpi_minus))
    with col2x:
        Cpi_plus = float(df_Cpi.loc[df_Cpi['ประเภท'] == Type_Building, 'Cpi_plus'])
        st.write(r'$C_{pi}⁺ = %.2f$'%(Cpi_plus))

st.write(r'### ค่าสัมประสิทธิ์ของหน่วยแรงลม, $C_p$')
tab1,tab2 = st.tabs(['Case 1','Case 2'])
with tab1:
    st.write(r'$ค่าสัมประสิทธิ์ของหน่วยแรงลมตามแนวแกน \quad x$')
    col1,col2,col3 = st.columns([0.1,0.3,0.6])
    with col2:
        # st.image('Cp.jpg' , use_column_width=True)
        if H/Widthx >= 1:
            Cpx_up = 0.8
            Cpx_down = -0.5
        elif H/Widthx < 1 and H/Widthx > 0.25:
            Cpx_up = 0.27*(H/Widthx + 2)
            Cpx_down = 0.27*(H/Widthx + 0.88)
        elif H/Widthx <= 0.25:
            Cpx_up = 0.6
            Cpx_down = -0.3
        Cpx_list = pd.DataFrame(Floors)
        Cpx_list['Cp,up'] = Cpx_up
        Cpx_list['Cp,up'] = Cpx_list['Cp,up'].round(2)
        Cpx_list['Cp,down'] = Cpx_down
        Cpx_list['Cp,down'] = Cpx_list['Cp,down'].round(2)
    col1,col2 = st.columns(2)      
    with col1:
        st.dataframe(Cpx_list, hide_index=True, use_container_width=True)
with tab2:
    st.write(r'$ค่าสัมประสิทธิ์ของหน่วยแรงลมตามแนวแกน \quad y$')
    col1,col2,col3 = st.columns([0.1,0.3,0.6])
    with col2:
        # st.image('Cp.jpg' , use_column_width=True)
        if H/Widthy >= 1:
            Cpy_up = 0.8
            Cpy_down = -0.5
        elif H/Widthy < 1 and H/Widthy > 0.25:
            Cpy_up = 0.27*(H/Widthy + 2)
            Cpy_down = 0.27*(H/Widthy + 0.88)
        elif H/Widthy <= 0.25:
            Cpy_up = 0.6
            Cpy_down = -0.3
        Cpy_list = pd.DataFrame(Floors)
        Cpy_list['Cp,up'] = Cpy_up
        Cpy_list['Cp,up'] = Cpy_list['Cp,up'].round(2)
        Cpy_list['Cp,down'] = Cpy_down
        Cpy_list['Cp,down'] = Cpy_list['Cp,down'].round(2)
    col1,col2 = st.columns(2)  
    with col1:
        st.dataframe(Cpy_list, hide_index=True, use_container_width=True)

Data = pd.DataFrame(Floors)

Floors['Z'] = Floor_list
Floors['Iw'] = Iw
Floors['q'] = q
Floors['q'] = Floors['q'].round(2)
Floors['Cg'] = Cg
Floors['Cg'] = Floors['Cg'].round(2)
Floors['Ce,up'] = Ce_list['Ce,up']
Floors['Ce,down'] = Ce_list['Ce,down']

st.write(r'### หน่วยแรงลมสุทธิ์, $P_{net}$')
tab1,tab2 = st.tabs(['Case 1','Case 2'])
with tab1:
    st.write(r'$หน่วยแรงลมสุทธิ์ตามแนวแกน \quad x$')
    Netx_pos = pd.DataFrame(Floors)
    Netx_pos['Cpi'] = Cpi_plus
    Netx_pos['Cp,up'] = Cpx_list['Cp,up']
    Netx_pos['Cp,down'] = Cpx_list['Cp,down']
    Netx_pos['Net Pressure'] = Cg*q*Iw*(Netx_pos['Ce,up']*(Netx_pos['Cp,up'] - Netx_pos['Cpi']) + abs(Netx_pos['Ce,down']*(Netx_pos['Cp,down'] - Netx_pos['Cpi'])))
    Netx_pos['Net Pressure'] = Netx_pos['Net Pressure'].round(2)
    st.markdown('')
    st.markdown('')
    col1,col2,col3 = st.columns(3)
    with col2:
        datanet_posx = pd.DataFrame(Data)
        datanet_posx['Net Pressure'] = Netx_pos['Net Pressure']
        chartnet_posx = alt.Chart(datanet_posx).mark_bar(size=Floor*12,color='white',stroke='red',strokeWidth=2).encode(x='Net Pressure',y=alt.Y('Floors', title='Floors'),).configure_mark(orient='horizontal').properties(height=Floor*61)
        st.altair_chart(chartnet_posx,use_container_width=True)
    st.write(r'$C_{pi}⁺$')
    st.dataframe(Netx_pos,hide_index=True, use_container_width=True)
    Netx_neg = pd.DataFrame(Floors)
    Netx_neg['Cpi'] = Cpi_minus
    Netx_neg['Cp,up'] = Cpx_list['Cp,up']
    Netx_neg['Cp,down'] = Cpx_list['Cp,down']
    Netx_neg['Net Pressure'] = Cg*q*Iw*(Netx_neg['Ce,up']*(Netx_neg['Cp,up'] - Netx_neg['Cpi']) + abs(Netx_neg['Ce,down']*(Netx_neg['Cp,down'] - Netx_neg['Cpi'])))
    Netx_neg['Net Pressure'] = Netx_neg['Net Pressure'].round(2)
    st.markdown('')
    st.markdown('')
    col1,col2,col3 = st.columns(3)
    with col2:
        datanet_negx = pd.DataFrame(Data)
        datanet_negx['Net Pressure'] = Netx_neg['Net Pressure']
        chartnet_negx = alt.Chart(datanet_negx).mark_bar(size=Floor*12,color='white',stroke='red',strokeWidth=2).encode(x='Net Pressure',y=alt.Y('Floors', title='Floors'),).configure_mark(orient='horizontal').properties(height=Floor*61)
        st.altair_chart(chartnet_negx,use_container_width=True)
    st.write(r'$C_{pi}⁻$')
    st.dataframe(Netx_neg,hide_index=True, use_container_width=True)
with tab2:
    st.write(r'$หน่วยแรงลมสุทธิ์ตามแนวแกน \quad y$')
    Nety_pos = pd.DataFrame(Floors)
    Nety_pos['Cpi'] = Cpi_plus
    Nety_pos['Cp,up'] = Cpy_list['Cp,up']
    Nety_pos['Cp,down'] = Cpy_list['Cp,down']
    Nety_pos['Net Pressure'] = Cg*q*Iw*(Nety_pos['Ce,up']*(Nety_pos['Cp,up'] - Nety_pos['Cpi']) + abs(Nety_pos['Ce,down']*(Nety_pos['Cp,down'] - Nety_pos['Cpi'])))
    Nety_pos['Net Pressure'] = Nety_pos['Net Pressure'].round(2)
    st.markdown('')
    st.markdown('')
    col1,col2,col3 = st.columns(3)
    with col2:
        datanet_posy = pd.DataFrame(Data)
        datanet_posy['Net Pressure'] = Nety_pos['Net Pressure']
        chartnet_posy = alt.Chart(datanet_posy).mark_bar(size=Floor*12,color='white',stroke='red',strokeWidth=2).encode(x='Net Pressure',y=alt.Y('Floors', title='Floors'),).configure_mark(orient='horizontal').properties(height=Floor*61)
        st.altair_chart(chartnet_posy,use_container_width=True)
    st.write(r'$C_{pi}⁺$')
    st.dataframe(Nety_pos,hide_index=True, use_container_width=True)
    Nety_neg = pd.DataFrame(Floors)
    Nety_neg['Cpi'] = Cpi_minus
    Nety_neg['Cp,up'] = Cpy_list['Cp,up']
    Nety_neg['Cp,down'] = Cpy_list['Cp,down']
    Nety_neg['Net Pressure'] = Cg*q*Iw*(Nety_neg['Ce,up']*(Nety_neg['Cp,up'] - Nety_neg['Cpi']) + abs(Nety_neg['Ce,down']*(Nety_neg['Cp,down'] - Nety_neg['Cpi'])))
    Nety_neg['Net Pressure'] = Nety_neg['Net Pressure'].round(2)
    st.markdown('')
    st.markdown('')
    col1,col2,col3 = st.columns(3)
    with col2:
        datanet_negy = pd.DataFrame(Data)
        datanet_negy['Net Pressure'] = Nety_neg['Net Pressure']
        chartnet_negy = alt.Chart(datanet_negy).mark_bar(size=Floor*12,color='white',stroke='red',strokeWidth=2).encode(x='Net Pressure',y=alt.Y('Floors', title='Floors'),).configure_mark(orient='horizontal').properties(height=Floor*61)
        st.altair_chart(chartnet_negy,use_container_width=True)
    st.write(r'$C_{pi}⁻$')
    st.dataframe(Nety_neg,hide_index=True, use_container_width=True)





