import streamlit as st
import pandas as pd
import numpy as np
from scipy import interpolate
from PIL import Image
import warnings
warnings.filterwarnings("ignore")


st.set_page_config(page_title='แรงลม มยผ', layout='wide', page_icon="🏗️")


def img_show(name, caption='', width=True):
    image = Image.open(name)
    return st.image(image, use_column_width=width, caption=caption)


st.write('# การคำนวณแรงลมสำหรับอาคารเตี้ย')
st.write('# ตามมาตรฐาน มยผ.1311-50 ด้วยวิธีอย่างง่าย')


# Step 0: มิติอาคาร
st.write('### มิติอาคาร')

col1, col2, col3, col4 = st.columns(4)
inputs = st.container()

with col1:
    H_roof = st.number_input(
        'ความสูงจั่วหลังคา , $H$roof [m]', value=8.65, step=0.1, min_value=0.0)
    st.write('ความสูงจั่วหลังคา = ', H_roof, " เมตร")

with col2:
    H = st.number_input(
        'ความสูงอาคาร(ชายคา),$H$[m]', value=6.00, step=0.1, min_value=0.0)
    st.write('ความสูงอาคาร(ชายคา) = ', H, " เมตร")

with col3:
    B = st.number_input(
        'ความกว้างในแนวตั้งฉากสันหลังคา,$B$[m]', value=60.00, step=0.1, min_value=0.0)
    st.write('ความกว้างในแนวตั้งฉากสันหลังคา = ', B, " เมตร")

with col4:
    W = st.number_input(
        'ความกว้างในแนวขนานสันหลังคา,$W$[m]', value=60.00, step=0.1, min_value=0.0)
    st.write('ความกว้างในแนวขนานสันหลังคา = ', W, " เมตร")

Ds = min(B, W)
st.write('ความกว้างด้านแคบที่สุด, $D_s = %.2f $' % (Ds))

slope = np.arctan((H_roof-H)/(0.5*B))*180.0/np.pi
st.write(r'Roof slope, $\theta = %.2f $' % (slope))

st.divider()

# Step 1: ค่าประกอบความสำคัญของแรงลม, Iw
df_important = pd.DataFrame({
    'ประเภทความสำคัญ': ['น้อย', 'ปกติ', 'มาก', 'สูงมาก'],
    'สภาวะจำกัดด้านกำลัง': [0.8, 1.0, 1.15, 1.15],
    'สภาวะจำกัดด้านการใช้งาน': [0.75, 0.75, 0.75, 0.75],
})

st.write('### ค่าประกอบความสำคัญของแรงลม, $Iw$')
col1, col2 = st.columns(2)
with col1:
    important_type = st.selectbox(
        label='ประเภทความสำคัญ', options=df_important['ประเภทความสำคัญ'], index=1)

with col2:
    cal_type = st.selectbox(
        label='ประเภทการออกแบบ', options=['สภาวะจำกัดด้านกำลัง', 'สภาวะจำกัดด้านการใช้งาน'])

with st.expander("See table"):
    st.dataframe(df_important, hide_index=True)

Iw = float(df_important.loc[df_important['ประเภทความสำคัญ']
                            == important_type, cal_type].values)
st.markdown(r'$Iw = %.2f$' % (Iw))

st.divider()

# Step 2: หน่วยแรงลมอ้างอิงเนื่องจากความเร็วลม , q
df_wind_speed = pd.DataFrame({
    'กลุ่ม': ['กลุ่มที่ 1', 'กลุ่มที่ 2', 'กลุ่มที่ 3', 'กลุ่มที่ 4A', 'กลุ่มที่ 4B'],
    'V50 [m/s]': [25, 27, 29, 25, 25],
    'T_F': [1.0, 1.0, 1.0, 1.2, 1.08],
})

st.write('### หน่วยแรงลมอ้างอิงเนื่องจากความเร็วลม , $q$')
st.latex(r'''
    q =  \frac{1}{2} \left(\frac{p}{g}\right) V^2
    ''')

P = 1.25
g = 9.81

st.write('ค่าคงที่, $p = %.2f {~kg/m^3}$' % (P))
st.write('ค่าคงที่, $g = %.2f {~m/s^2}$' % (g))


area_group = st.selectbox(
    label='กลุ่มพื้นที่', options=df_wind_speed['กลุ่ม'], index=2)

with st.expander("See table"):
    st.dataframe(df_wind_speed, hide_index=True)

V50 = df_wind_speed.loc[df_wind_speed['กลุ่ม']
                        == area_group, 'V50 [m/s]'].values
T_F = df_wind_speed.loc[df_wind_speed['กลุ่ม'] == area_group, 'T_F'].values

if cal_type == 'สภาวะจำกัดด้านกำลัง':
    V = V50*T_F
    st.markdown(
        r'$V_{50} = %.2f \mathrm{~m/s,} \quad T_F = %.2f$' % (V50, T_F))
    st.markdown(
        r'$\overline{V} = V_{50} T_F = %.2f \times %.2f = %.2f \mathrm{~m/s}$' % (V50, T_F, V))
else:
    V = V50
    st.markdown(r'$V_{50} = %.2f \mathrm{~m/s}$' % (V50))
    st.markdown(r'$\overline{V} = V_{50} T_F = %.2f \mathrm{~m/s}$' % (V))

q = float(0.5*(P/g)*(V**2))
st.markdown(
    r'$q = \frac{1}{2} \left( \frac{p}{g} \right) \overline{V}^{2} = \frac{1}{2} \left( \frac{%.2f \mathrm{~kg/m^3}}{%.2f \mathrm{~m/s^2}} \right) \left( %.2f \mathrm{~m/s} \right)^{2} = %.2f \mathrm{~kg/m^2}$' % (P, g, V, q))

st.divider()

# Step 3: ค่าประกอบเนื่องจากสภาพถูมิประเทศ , Ce
st.write('### ค่าประกอบเนื่องจากสภาพถูมิประเทศ , $Ce$')

df_terrain = pd.DataFrame({
    'ความสูงจากพื้นดิน':
    [
        'สูงไม่เกิน 6 เมตร',
        'สูงเกิน 6 เมตรแต่ไม่เกิน 10 เมตร',
        'สูงเกิน 10 เมตรแต่ไม่เกิน 20 เมตร',
        'สูงเกิน 20 เมตรแต่ไม่เกิน 30 เมตร',
        'สูงเกิน 30 เมตรแต่ไม่เกิน 40 เมตร',
        'สูงเกิน 40 เมตรแต่ไม่เกิน 60 เมตร',
        'สูงเกิน 60 เมตรแต่ไม่เกิน 80 เมตร',
    ],
    'สภาพภูมิประเทศแบบ A':
    [
        0.90, 1.00, 1.15, 1.25, 1.32, 1.43, 1.52
    ],
    'สภาพภูมิประเทศแบบ B':
    [
        0.70, 0.70, 0.82, 0.92, 1.00, 1.13, 1.24
    ],
})

terrain_type = st.selectbox(
    label='ความสูงจากพื้นดิน', options=df_terrain['ความสูงจากพื้นดิน'], index=2)

with st.expander("See table"):
    st.dataframe(df_terrain, hide_index=True)

st.write('### สภาพภูมิประเทศแบบ A')
Ce_A = df_terrain.loc[df_terrain['ความสูงจากพื้นดิน']
                      == terrain_type, 'สภาพภูมิประเทศแบบ A'].values
st.markdown(r'$Ce_A = %.2f$' % (Ce_A))

st.write('### สภาพภูมิประเทศแบบ B')
Ce_B = df_terrain.loc[df_terrain['ความสูงจากพื้นดิน']
                      == terrain_type, 'สภาพภูมิประเทศแบบ B']
st.markdown(r'$Ce_B = %.2f$' % (Ce_B))

# select A or B terrain
terrain = st.selectbox(
    label='เลือกสภาพภูมิประเทศ', options=['สภาพภูมิประเทศแบบ A', 'สภาพภูมิประเทศแบบ B'], index=1)


# float Ce

if terrain == 'สภาพภูมิประเทศแบบ A':
    Ce = float(Ce_A)
else:
    Ce = float(Ce_B)


st.markdown(r'$Ce = %.2f$' % (Ce))

st.divider()

# Step 4.1: แรงลมภายในอาคาร Pi
st.write('### แรงลมภายในอาคาร, $Pi$')
st.latex(r'''
    Pi =  lw \cdot q \cdot Ce \cdot Cgi \cdot Cpi
    ''')

Cgi = 2.0

df_internal_pressure = pd.DataFrame({
    'ประเภทของอาคาร': ['อาคารที่ปารศจากช่องเปิดขนาดใหญ่', 'อาคารที่มีการรั่วซึมกระจายไม่สม่ำเสมอ', 'อาคารที่มีช่องเปิดขนาดใหญ่'],
    'MinCpi': [-0.15, -0.45, -0.70],
    'MaxCpi': [0.00, 0.30, 0.70],
})

internal_pressure_type = st.selectbox(
    label='ประเภทของอาคาร', options=df_internal_pressure['ประเภทของอาคาร'], index=2)

with st.expander("See table"):
    st.dataframe(df_internal_pressure, hide_index=True)

MinCpi = float(df_internal_pressure.loc[df_internal_pressure['ประเภทของอาคาร']
                                        == internal_pressure_type, 'MinCpi'].values)
MaxCpi = float(df_internal_pressure.loc[df_internal_pressure['ประเภทของอาคาร']
                                        == internal_pressure_type, 'MaxCpi'].values)

st.markdown(r'ค่าประกอบเนื่องจากการกรรโชกของลม $Cgi = %.2f$' % (Cgi))
st.markdown(r'ค่าสัมประสิทธิ์แรงลมภายในอาคาร $Cpi = %.2f$ |  $%.2f$' %
            (MinCpi, MaxCpi))
st.markdown(r'ค่าสัมประสิทธิ์ของหน่วยแรงลม $CgiCpi = %.2f$ |  $%.2f$' %
            (MinCpi * Cgi, MaxCpi * Cgi))

leftValue = Iw*q*Ce*(MaxCpi * Cgi)
rightValue = Iw*q*Ce*(MinCpi * Cgi)

st.markdown(r'__ดังนั้นแรงลมภายในอาคาร $= IwqCeCgiCpi = %.2f | %.2f$__' %
            (leftValue, rightValue))

st.divider()

# Step 4.2: หา CgCp และ แรงลมภายนอกอาคาร P
st.markdown(r'### ค่าสัมประสิทธิ์ของหน่วยแรงลมภายนอก, $C_p C_g$')

df_case1 = pd.DataFrame({
    'Slope min [deg]': [0, 20, 30, 90],
    'Slope max [deg]': [5, 20, 45, 90],
    '1': [0.75, 1.0, 1.05, 1.05],
    '1E': [1.15, 1.5, 1.3, 1.3],
    '2': [-1.3, -1.3, 0.4, 1.05],
    '2E': [-2.0, -2.0, 0.5, 1.3],
    '3': [-0.7, -0.9, -0.8, -0.7],
    '3E': [-1.0, -1.3, -1.0, -0.9],
    '4': [-0.55, -0.8, -0.7, -0.7],
    '4E': [-0.8, -1.2, -0.9, -0.9],
})

df_case2 = pd.DataFrame({
    'Slope min [deg]': [0],
    'Slope max [deg]': [90],
    '1': [-0.85],
    '1E': [-0.9],
    '2': [-1.3],
    '2E': [-2.0],
    '3': [-0.7],
    '3E': [-1.0],
    '4': [-0.85],
    '4E': [-0.9],
    '5': [0.75],
    '5E': [1.15],
    '6': [-0.55],
    '6E': [-0.8],
})


zone_list = df_case1.columns
zone_list = ['Slope [deg]'] + zone_list[2:].to_list()


def interpolate_y(index):
    x_data = [float(df_case1['Slope max [deg]'][index]),
              float(df_case1['Slope min [deg]'][index+1])]
    aa = df_case1.iloc[index, 2:].to_list()
    bb = df_case1.iloc[index+1, 2:].to_list()
    y_all = zip(aa, bb)

    y_interpolate = []
    for y_data in y_all:
        f = interpolate.interp1d(x_data, y_data)
        y_interpolate.append(round(f([slope])[0], 2))

    df = pd.DataFrame(data=[round(slope, 2)] + y_interpolate)
    df = df.T
    df.columns = zone_list

    return df


if slope > 5.0 and slope < 20.0:
    df_CpCg = interpolate_y(0)
elif slope > 20.0 and slope < 30.0:
    df_CpCg = interpolate_y(1)
elif slope > 45.0 and slope < 90.0:
    df_CpCg = interpolate_y(2)
elif slope >= 0.0 and slope <= 5.0:
    df_CpCg = pd.DataFrame(
        data=[round(slope, 2)] + df_case1.iloc[0, 2:].to_list())
    df_CpCg = df_CpCg.T
    df_CpCg.columns = zone_list
elif slope == 20.0:
    df_CpCg = pd.DataFrame(
        data=[round(slope, 2)] + df_case1.iloc[1, 2:].to_list())
    df_CpCg = df_CpCg.T
    df_CpCg.columns = zone_list
elif slope >= 30.0 and slope <= 45.0:
    df_CpCg = pd.DataFrame(
        data=[round(slope, 2)] + df_case1.iloc[2, 2:].to_list())
    df_CpCg = df_CpCg.T
    df_CpCg.columns = zone_list
elif slope == 90.0:
    df_CpCg = pd.DataFrame(
        data=[round(slope, 2)] + df_case1.iloc[3, 2:].to_list())
    df_CpCg = df_CpCg.T
    df_CpCg.columns = zone_list


st.markdown(
    '**กรณีที่ 1:** ทิศทางการพัดของลมโดยทั่วไปอยู่ในแนว**ตั้งฉาก**กับสันหลังคา')
col1x, _, _ = st.columns([0.5, 0.5, 0.5])
with col1x:
    img_show('CpCg_case1.png')

p_case_1 = df_CpCg.iloc[0, 1:].to_list()

for i in range(len(p_case_1)):
    p_case_1[i] = (Iw * q * Ce * p_case_1[i])

p_case_1.insert(0, 'หน่วยแรงลมภายนอกอาคาร, P กิโลกรัมต่อตารางเมตร')
df_p_case_1 = pd.DataFrame(p_case_1)

windOutside_case_1 = df_p_case_1.transpose()

windOutside_case_1.columns = df_CpCg.columns

updated_df_CpCg = pd.concat(
    [df_CpCg, windOutside_case_1]).reset_index(drop=True)

st.dataframe(updated_df_CpCg, hide_index=True, use_container_width=True)

with st.expander('See table'):
    st.dataframe(df_case1, hide_index=True, use_container_width=True)

st.divider()

# Step 5 หน่วยแรงลมสุทธิ


st.markdown(r'### หน่วยแรงลมสุทธิ')
st.write("กรณีที่ 1: ทิศทางลมอยู่แนวตั้งฉากกับสันหลังคา")
# st.dataframe(df_p_case_1[1:])

symmetricalInertia_1 = df_p_case_1[1:].values.tolist()
symmetricalInertia_2 = df_p_case_1[1:].values.tolist()

for i in range(len(symmetricalInertia_1)):
    print(symmetricalInertia_1[i][0],"-",leftValue,"=",symmetricalInertia_1[i][0] - leftValue)
    symmetricalInertia_1[i] = symmetricalInertia_1[i][0] - leftValue
    symmetricalInertia_2[i] = symmetricalInertia_2[i][0] - rightValue

data = {
    'พื้นผิวของอาคาร': ['1', '1E', '2', '2E', '3', '3E', '4', '4E'],
    'แรงดันภายในเป็นลบ (กิโลกรัมเมตร^2)': symmetricalInertia_1,
    'แรงดันภายในเป็นบวก (กิโลกรัมเมตร^2)': symmetricalInertia_2,
}
df = pd.DataFrame(data)

st.dataframe(df, hide_index=True, use_container_width=True)
