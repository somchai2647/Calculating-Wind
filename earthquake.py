import streamlit as st
import pandas as pd
import numpy as np
from scipy import interpolate
from PIL import Image
import plotly.graph_objects as go
from scipy import interpolate


def img_show(name, caption='', width=True):
    image = Image.open(name)
    return st.image(image, use_column_width=width, caption=caption, )


def main():

    st.write('# มยผ.1301/1302-61')

    st.write('### ตัวประกอบความสำคัญและประเภทของอาคาร')
    important_dict = {
        'น้อย': 1.0,
        'ปกติ': 1.0,
        'มาก': 1.25,
        'สูงมาก': 1.5,
    }
    important = st.selectbox(label='ประเภทความสำคัญ',
                             options=important_dict.keys(), key='important')
    I = important_dict[important]  # กำหนดค่า I จาก dictionary
    st.write(r'Important factor, $I = %.2f$' % (I))

    st.write(
        '### วิธีการวิเคราะห์โครงสร้างเพื่อคำนวณผลของแรงแผ่นดินไหว โดยวิธีสถิตย์เทียบเท่า')
    # สร้าง list ของวิธีการวิเคราะห์
    cal_list = ['วิธีสถิตย์เทียบเท่า', 'วิธีเชิงพลศาสตร์']

    cal = "วิธีสถิตย์เทียบเท่า"  # 👈 ตั้งค่าเริ่มต้น

    st.write('### รายละเอียดโครงสร้าง')
    col1, col2, col3 = st.columns(3)

    with col1:
        structure_list = ['คอนกรีตเสริมเหล็ก', 'เหล็ก']
        structure = st.radio(label='ประเภทโครงสร้าง',
                             options=structure_list, index=0, key='structure')  # เลือกประเภทโครงสร้าง
    with col2:
        if structure == structure_list[0]:  # เมื่อเลือกคอนกรีตเสริมเหล็ก
            damping_list = ['5.0%', '2.5%']  # กำหนดค่าความหน่วง
        else:
            damping_list = ['2.5%']  # กำหนดค่าความหน่วง
        damping = st.radio(label='ความหน่วง',
                           options=damping_list, index=0, key='damping')  # เลือกค่าความหน่วง
    with col3:
        H = st.number_input(
            # ใส่ค่าความสูงของอาคาร
            label=r'ความสูงอาคารวัดจากพื้นดิน, $H \mathrm{~[m]}$', min_value=0.0, value=6.0, key='H')

    st.write('### ความเร่งตอบสนองเชิงสเปกตรัม')

    bkk = st.checkbox('พื้นที่ในแอ่งกรุงเทพฯ หรือไม่ ???',
                      value=False, key='bkk')  # เลือกเขตพื้นที่

    if not bkk:  # ถ้าไม่ใช่เขตพื้นที่กรุงเทพฯ

        # อ่านข้อมูลจากไฟล์ excel
        df_SsS1 = pd.read_excel('แผ่นดินไหว_table.xlsx', sheet_name='SsS1')

        col1, col2, col3 = st.columns(3)  # แบ่งคอลัมน์เป็น 3 ส่วน
        with col1:
            province = st.selectbox(
                # เลือกจังหวัด
                label='จังหวัด', options=df_SsS1['จังหวัด'].unique(), index=12, key='province')
        with col2:
            district = st.selectbox(
                # เลือกอำเภอ
                label='อำเภอ', options=df_SsS1.loc[df_SsS1['จังหวัด'] == province, 'อำเภอ'], key='district')

        Ss = df_SsS1.loc[(df_SsS1['จังหวัด'] == province) & (
            df_SsS1['อำเภอ'] == district), 'Ss'].iloc[0]  # ค่า Ss จากข้อมูล
        S1 = df_SsS1.loc[(df_SsS1['จังหวัด'] == province) & (
            df_SsS1['อำเภอ'] == district), 'S1'].iloc[0]  # ค่า S1 จากข้อมูล

        st.write(r'$S_s = %.3f \> g$' % (Ss))
        st.write(r'$S_1 = %.3f \> g$' % (S1))

        st.write(
            '### ปรับแก้ค่าระดับความรุนแรงจากแรงแผ่นดินไหวเนื่องจากผลของประเภทชั้นดิน')

        soil_type = st.selectbox(label='ประเภทชั้นดิน', options=[
                                 'A', 'B', 'C', 'D', 'E', 'F'], index=0, key='soil_type')  # เลือกประเภทชั้นดิน

        def FaFv(df, S):  # ฟังก์ชันคำนวณค่า Fa และ Fv
            if S <= df['index'].min():  # ถ้าค่า S น้อยกว่าค่าน้อยสุดในข้อมูล
                # ให้ค่า F เท่ากับค่าที่น้อยสุดในข้อมูล
                F = df[soil_type].iloc[0]
            elif S >= df['index'].max():  # ถ้าค่า S มากกว่าค่ามากสุดในข้อมูล
                # ให้ค่า F เท่ากับค่าที่มากสุดในข้อมูล
                F = df[soil_type].iloc[-1]
            else:
                # ค่า y0 จากข้อมูลที่น้อยกว่า S
                y0 = df.loc[df['index'] <= S, soil_type].iloc[-1]
                # ค่า y1 จากข้อมูลที่มากกว่า S
                y1 = df.loc[df['index'] >= S, soil_type].iloc[0]

                # ค่า x0 จากข้อมูลที่น้อยกว่า S
                x0 = df.loc[df['index'] <= S, 'index'].iloc[-1]
                # ค่า x1 จากข้อมูลที่มากกว่า S
                x1 = df.loc[df['index'] >= S, 'index'].iloc[0]

                x_data = [x0, x1]  # ข้อมูล x
                y_data = [y0, y1]  # ข้อมูล y

                # ฟังก์ชัน interpolate
                f = interpolate.interp1d(x_data, y_data)

                F = f([S])[0]  # คำนวณค่า F

            return F  # คืนค่า F

        # อ่านข้อมูลจากไฟล์ excel Fa
        df_Fa = pd.read_excel('แผ่นดินไหว_table.xlsx', sheet_name='Fa')
        # ตั้งค่า index ของข้อมูล
        df_Fa.set_index('ประเภทชั้นดิน', inplace=True)
        # ทำการ transpose ข้อมูล คือ สลับแถวกับคอลัมน์
        df_Fa = df_Fa.T.reset_index().astype('float')

        # อ่านข้อมูลจากไฟล์ excel โดยเลือก sheet ที่ชื่อ Fv
        df_Fv = pd.read_excel('แผ่นดินไหว_table.xlsx', sheet_name='Fv')
        # ตั้งค่า index ของข้อมูล
        df_Fv.set_index('ประเภทชั้นดิน', inplace=True)
        # ทำการ transpose ข้อมูล คือ สลับแถวกับคอลัมน์
        df_Fv = df_Fv.T.reset_index().astype('float')

        Fa = FaFv(df_Fa, Ss)  # คำนวณค่า Fa
        Fv = FaFv(df_Fv, S1)  # คำนวณค่า Fv

        st.write(r'$F_a = %.3f \> g$' % (Fa))  # แสดงค่า Fa
        st.write(r'$F_v = %.3f \> g$' % (Fv))  # แสดงค่า Fv

        SMS = Fa*Ss  # คำนวณค่า SMS
        SM1 = Fv*S1  # คำนวณค่า SM1

        st.write(
            r'$S_{MS} = F_{a} S_{s} = %.3f \times %.3f = %.3f \> g$' % (Fa, Ss, SMS))
        st.write(
            r'$S_{M1} = F_{v} S_{1} = %.3f \times %.3f = %.3f \> g$' % (Fv, S1, SM1))

        st.write('### ปรับแก้ค่าระดับความรุนแรงจากแรงแผ่นดินไหวสำหรับออกแบบ')

        SDS = (2/3)*SMS  # คำนวณค่า SDS
        SD1 = (2/3)*SM1  # คำนวณค่า SD1

        st.write(
            r'$S_{DS} = \frac{2}{3} S_{MS} = \frac{2}{3} \times %.3f = %.3f \> g$' % (SMS, SDS))
        st.write(
            r'$S_{D1} = \frac{2}{3} S_{M1} = \frac{2}{3} \times %.3f = %.3f \> g$' % (SM1, SD1))

    else:
        with (st.expander('การแบ่งโซนพื้นที่ในแอ่งกรุงเทพฯ')):
            img_show('eq_bkk_zone.png')  # แสดงรูปภาพ

        zone = st.selectbox(label='Zone', options=np.arange(
            1, 11), key='zone')  # เลือกโซน

        sheet_name_ = 'bkk_equivalent'  # ชื่อ sheet ของข้อมูล

        if damping == '5.0%':  # ถ้าเลือกค่าความหน่วง 5.0%
            # กำหนดชื่อ sheet ของข้อมูล โดยเพิ่ม _5.0 ต่อท้าย
            sheet_name = sheet_name_ + '_5.0'
        else:
            sheet_name = sheet_name_ + '_2.5'  # ถ้าไม่ใช่ 5.0% ก็เป็น 2.5% แทน

        # อ่านข้อมูลจากไฟล์ excel
        df_bkk = pd.read_excel('แผ่นดินไหว_table.xlsx', sheet_name=sheet_name)

        col = df_bkk.columns  # คอลัมน์ของข้อมูล
        df_bkk = pd.melt(
            # ทำการ transpose ข้อมูล คือ สลับแถวกับคอลัมน์
            df_bkk, id_vars=col[0], value_vars=col[1:], var_name='T', value_name='Sa').astype('float')

        SDS = df_bkk.loc[(df_bkk['zone'] == zone) & (
            df_bkk['T'] == 0.2), 'Sa'].iloc[0]  # คำนวณค่า SDS
        SD1 = df_bkk.loc[(df_bkk['zone'] == zone) & (
            df_bkk['T'] == 1.0), 'Sa'].iloc[0]  # คำนวณค่า SD1

        st.write(r'$S_{DS} = %.3f \> g$' % (SDS))
        st.write(r'$S_{D1} = %.3f \> g$' % (SD1))

    st.write('### คำนวณค่าคาบการสั่นพื้นฐานโดยประมาณ')
    # calculate T of structure
    if structure == structure_list[0]:  # เมื่อโครงสร้างเป็น คอนกรีตเสริมเหล็ก
        T_structure = 0.02*H  # คำนวณค่า T ของโครงสร้าง
        st.write('อาคาร', structure, r'$\qquad  T = 0.02H = 0.02 \times %.2f \mathrm{~m} = %.3f \mathrm{~sec}$' % (
            H, T_structure))
    else:  # เมื่อโครงสร้างเป็น เหล็ก
        T_structure = 0.03*H  # คำนวณค่า T ของโครงสร้าง
        st.write('อาคาร', structure, r'$\qquad  T = 0.03H = 0.03 \times %.2f \mathrm{~m} = %.3f \mathrm{~sec}$' % (
            H, T_structure))

    st.write('### ประเภทการออกแบบต้านทานแผ่นดินไหว')
    st.write(
        'การแบ่งประเภทการออกแบบต้านทานแผ่นดินไหวโดยพิจารณาจากค่า $S_{DS}$ และ $S_{D1}$ นี้ กำหนดให้พิจารณาอัตราส่วนความหน่วงเท่ากับร้อยละ 5 **สำหรับอาคารทุกประเภท**')

    type_dict = {
        '1': 'ก',
        '2': 'ข',
        '3': 'ค',
        '4': 'ง',
    }  # สร้าง dictionary ของประเภทการออกแบบต้านทานแผ่นดินไหว

    def type161162TS(SDS, SD1):  # ฟังก์ชันคำนวณประเภทการออกแบบต้านทานแผ่นดินไหว
        # อ่านข้อมูลจากไฟล์ excel โดยเลือก sheet ที่ชื่อ T1.6-1
        df = pd.read_excel('แผ่นดินไหว_table.xlsx', sheet_name='T1.6-1')
        df = pd.melt(df, id_vars=['min', 'max'], value_vars=[
                     # ทำการ transpose ข้อมูล คือ สลับแถวกับคอลัมน์
                     'น้อย', 'ปกติ', 'มาก', 'สูงมาก'], var_name='important', value_name='type')

        # คำนวณค่าประเภทการออกแบบต้านทานแผ่นดินไหว
        type161 = df.loc[(df['min'] <= SDS) & (df['max'] > SDS) & (
            df['important'] == important), 'type'].iloc[0]

        # อ่านข้อมูลจากไฟล์ excel โดยเลือก sheet ที่ชื่อ T1.6-2
        df = pd.read_excel('แผ่นดินไหว_table.xlsx', sheet_name='T1.6-2')

        # ทำการ transpose ข้อมูล คือ สลับแถวกับคอลัมน์
        df = pd.melt(df, id_vars=['min', 'max'], value_vars=[
                     'น้อย', 'ปกติ', 'มาก', 'สูงมาก'], var_name='important', value_name='type')

        # คำนวณค่าประเภทการออกแบบต้านทานแผ่นดินไหว
        type162 = df.loc[(df['min'] <= SD1) & (df['max'] > SD1) & (
            df['important'] == important), 'type'].iloc[0]

        if SD1 <= SDS:  # ถ้าค่า SD1 น้อยกว่าหรือเท่ากับค่า SDS
            TS = SD1/SDS
        else:  # ถ้าค่า SD1 มากกว่าค่า SDS
            TS = 1.0

        return type161, type162, TS  # คืนค่าประเภทการออกแบบต้านทานแผ่นดินไหว

    # ถ้าเป็นเขตพื้นที่กรุงเทพฯ และความหน่วง 2.5%
    if bkk and damping == '2.5%':

        df_bkkx = pd.read_excel('แผ่นดินไหว_table.xlsx',
                                sheet_name=sheet_name_ + '_5.0')  # อ่านข้อมูลจากไฟล์ excel

        # ทำการ transpose ข้อมูล คือ สลับแถวกับคอลัมน์ และเปลี่ยนชื่อคอลัมน์
        df_bkkx = pd.melt(
            df_bkkx, id_vars=col[0], value_vars=col[1:], var_name='T', value_name='Sa').astype('float')

        SDSx = df_bkkx.loc[(df_bkkx['zone'] == zone) & (
            df_bkkx['T'] == 0.2), 'Sa'].iloc[0]  # คำนวณค่า SDS
        SD1x = df_bkkx.loc[(df_bkkx['zone'] == zone) & (
            df_bkkx['T'] == 1.0), 'Sa'].iloc[0]  # คำนวณค่า SD1

        st.write('สำหรับอัตราส่วนความหน่วงเท่ากับ 5%')
        st.write(r'$S_{DS} = %.3f \> g$' % (SDSx))
        st.write(r'$S_{D1} = %.3f \> g$' % (SD1x))

        # คำนวณประเภทการออกแบบต้านทานแผ่นดินไหว function จากบรรทัดที่ 205
        type161, type162, TTSS = type161162TS(SDSx, SD1x)

    else:
        # คำนวณประเภทการออกแบบต้านทานแผ่นดินไหว function จากบรรทัดที่ 205
        type161, type162, TTSS = type161162TS(SDS, SD1)

    if not bkk:  # ถ้าไม่ใช่เขตพื้นที่กรุงเทพฯ
        if T_structure < 0.8*TTSS:  # ถ้าค่า T น้อยกว่า 0.8 ค่า TTSS
            st.write(r'สำหรับ $\quad T = %.3f \mathrm{~sec} \quad < \quad 0.8 T_s = 0.8 \times %.3f = %.3f \mathrm{~sec}$' % (
                T_structure, TTSS, 0.8*TTSS))
            st.write(
                r'พิจารณาประเภทการออกแบบต้านทานแผ่นดินไหวตามเกณฑ์ในตารางที่ 1.6-1 เท่านั้น')
            type_num = type161  # กำหนดค่า type_num เท่ากับ type161
        else:  # ถ้าค่า T มากกว่าหรือเท่ากับ 0.8 ค่า TTSS
            st.write(r'สำหรับ $\quad T = %.3f \mathrm{~sec} \quad \ge \quad 0.8 T_s = 0.8 \times %.3f = %.3f \mathrm{~sec}$' % (
                T_structure, TTSS, 0.8*TTSS))
            st.write(
                r'พิจารณาประเภทการออกแบบต้านทานแผ่นดินไหวที่เข้มงวดกว่าตามเกณฑ์ในตารางที่ 1.6-1 และ 1.6-2')
            # กำหนดค่า type_num เท่ากับค่าที่มากที่สุดระหว่าง type161 และ type162
            type_num = max(type161, type162)
    else:  # ถ้าเป็นเขตพื้นที่กรุงเทพฯ
        if T_structure <= 0.5:  # ถ้าค่า T น้อยกว่าหรือเท่ากับ 0.5
            st.write(r'สำหรับ $\quad T = %.3f \mathrm{~sec} \quad \le \quad 0.5 \mathrm{~sec}$' % (
                T_structure))
            st.write(
                r'พิจารณาประเภทการออกแบบต้านทานแผ่นดินไหวตามเกณฑ์ในตารางที่ 1.6-1 เท่านั้น')
            type_num = type161  # กำหนดค่า type_num เท่ากับ type161
        else:  # ถ้าค่า T มากกว่า 0.5
            st.write(r'สำหรับ $\quad T = %.3f \mathrm{~sec} \quad > \quad 0.5 \mathrm{~sec}$' % (
                T_structure))
            st.write(
                r'พิจารณาประเภทการออกแบบต้านทานแผ่นดินไหวตามเกณฑ์ในตารางที่ 1.6-2 เท่านั้น')
            type_num = type162  # กำหนดค่า type_num เท่ากับ type162

    # กำหนดค่า type เท่ากับค่าใน dictionary ของประเภทการออกแบบต้านทานแผ่นดินไหว โดยใช้ค่า type_num เป็น key
    type = type_dict[str(type_num)]

    st.write(r'ประเภทการออกแบบต้านแผ่นดินไหว: <span style="color:blue">**ประเภท %s**</span>' %
             (type), unsafe_allow_html=True)

    st.write('### ค่าประกอบตามประเภทโครงสร้าง')
    col1, col2, col3 = st.columns(3)
    with col1:
        R = st.number_input(
            label='Response Modification Factor, $R$', min_value=0.0, value=8.0, key='R')
    with col2:
        omega0 = st.number_input(
            label='System Overstrength Factor, $\Omega_0$', min_value=0.0, value=3.0, key='omega0')
    with col3:
        Cd = st.number_input(
            label='Deflection Amplification Factor, $C_d$', min_value=0.0, value=5.5, key='Cd')

    st.write('### ค่าความเร่งตอบสนองเชิงสเปกตรัมสำหรับออกแบบ')
    # graph data
    if not bkk:  # ถ้าไม่ใช่เขตพื้นที่กรุงเทพฯ
        if cal == cal_list[0]:  # ถ้าเลือกวิธีสถิตย์เทียบเท่า
            if SD1 <= SDS:  # ถ้าค่า SD1 น้อยกว่าหรือเท่ากับค่า SDS
                T0 = 0.0  # กำหนดค่า T0 เท่ากับ 0
                Ts = SD1/SDS  # คำนวณค่า Ts จากสมการ Ts = SD1/SDS  โดยที่ SD1 และ SDS คือค่าที่ได้จากข้อมูล
                # สร้าง array ของค่า T โดยเริ่มจาก 0 ถึง Ts และเพิ่มค่าทีละ 0.1 จนถึง 2.0
                T_data = np.append([T0, Ts], np.arange(round(Ts, 1), 2.1, 0.1))

                # สร้าง array ของค่า Sa โดยเริ่มจาก SDS ถึง SDS และเพิ่มค่า SDS จนถึง SD1
                S_data = np.array([SDS, SDS])

                for T in T_data:  # วนลูปเพื่อคำนวณค่า Sa จากข้อมูล
                    if T > Ts:  # ถ้าค่า T มากกว่าค่า Ts
                        # เพิ่มค่า SD1/T ใน array
                        S_data = np.append(S_data, [SD1/T])

                # calculate Sa of structure
                if T_structure <= Ts:  # ถ้าค่า T น้อยกว่าหรือเท่ากับค่า Ts
                    Sa_structure = SDS  # กำหนดค่า Sa_structure เท่ากับ SDS
                else:
                    Sa_structure = SD1/T_structure  # คำนวณค่า Sa_structure จากสมการ SD1/T_structure

            elif SD1 > SDS:  # ถ้าค่า SD1 มากกว่าค่า SDS
                T0 = 0.2  # กำหนดค่า T0 เท่ากับ 0.2
                Ts = 1.0  # กำหนดค่า Ts เท่ากับ 1.0
                # สร้าง array ของค่า T โดยเริ่มจาก 0 ถึง 2.0
                T_data = np.append([0, T0, Ts], np.arange(1.1, 2.1, 0.1))
                # สร้าง array ของค่า Sa โดยเริ่มจาก SDS ถึง SDS และเพิ่มค่า SDS จนถึง SD1
                S_data = np.array([SDS, SDS, SD1])

                for T in T_data:  # วนลูปเพื่อคำนวณค่า Sa จากข้อมูล
                    if T > Ts:  # ถ้าค่า T มากกว่าค่า Ts
                        # เพิ่มค่า SD1/T ใน array
                        S_data = np.append(S_data, [SD1/T])

                # calculate Sa of structure
                if T_structure <= T0:  # ถ้า T_structure น้อยกว่าหรือเท่ากับ T0, Sa_structure จะเท่ากับ SDS
                    Sa_structure = SDS
                elif T_structure > T0 and T_structure <= Ts:
                    # สร้างฟังก์ชันการแก้ไขระหว่าง T0 และ Ts
                    f = interpolate.interp1d([T0, Ts], [SDS, SD1])
                    # คำนวณ Sa_structure โดยใช้ฟังก์ชันการแก้ไขที่สร้างขึ้น
                    Sa_structure = f(T_structure)
                else:
                    # ถ้า T_structure มากกว่า Ts, Sa_structure จะเท่ากับ SD1 หารด้วย T_structure
                    Sa_structure = SD1/T_structure

        # adjust data for 2.5% damping ratio
        if damping == '2.5%':  # ถ้าเลือกค่าความหน่วง 2.5%
            for i in range(len(T_data)):  # วนลูปเพื่อปรับค่า S_data ตามค่า T_data
                if T_data[i] >= T0:  # ถ้า T_data ที่ i มากกว่าหรือเท่ากับ T0
                    # ปรับค่า S_data ที่ i โดยการหารด้วย 0.85
                    S_data[i] = S_data[i]/0.85
                else:  # ถ้า T_data ที่ i น้อยกว่า T0
                    # ปรับค่า S_data ที่ i ตามสมการนี้
                    S_data[i] = SDS*(3.88*T_data[i]/Ts + 0.4)

            if T_structure >= T0:  # ถ้า T_structure มากกว่าหรือเท่ากับ T0
                Sa_structure = Sa_structure/0.85  # ปรับค่า Sa_structure โดยการหารด้วย 0.85
            else:  # ถ้า T_structure น้อยกว่า T0
                # ปรับค่า Sa_structure ตามสมการนี้
                Sa_structure = SDS*(3.88*T_structure/Ts + 0.4)

    elif bkk:  # ถ้าเป็นเขตพื้นที่กรุงเทพฯ

        # ดึงข้อมูลค่า T ที่มี zone ตรงกับที่กำหนด
        T_data = df_bkk.loc[df_bkk['zone'] == zone, 'T']
        # ดึงข้อมูลค่า Sa ที่มี zone ตรงกับที่กำหนด
        S_data = df_bkk.loc[df_bkk['zone'] == zone, 'Sa']

        y0 = df_bkk.loc[(df_bkk['zone'] == zone) & (
            # ค้นหาค่า Sa สุดท้ายที่ T น้อยกว่าหรือเท่ากับ T_structure ใน zone ที่กำหนด
            df_bkk['T'] <= T_structure), :].iloc[-1]['Sa']
        y1 = df_bkk.loc[(df_bkk['zone'] == zone) & (
            # ค้นหาค่า Sa แรกที่ T มากกว่าหรือเท่ากับ T_structure ใน zone ที่กำหนด
            df_bkk['T'] >= T_structure), :].iloc[0]['Sa']
        x0 = df_bkk.loc[(df_bkk['zone'] == zone) & (
            # ค้นหาค่า T สุดท้ายที่น้อยกว่าหรือเท่ากับ T_structure ใน zone ที่กำหนด
            df_bkk['T'] <= T_structure), :].iloc[-1]['T']
        x1 = df_bkk.loc[(df_bkk['zone'] == zone) & (
            # ค้นหาค่า T แรกที่มากกว่าหรือเท่ากับ T_structure ใน zone ที่กำหนด
            df_bkk['T'] >= T_structure), :].iloc[0]['T']

        # log interpolation
        # สร้างฟังก์ชันการแก้ไขระหว่าง log10(x0) และ log10(x1) โดยใช้ log10(y0) และ log10(y1) เป็นค่า y
        f = interpolate.interp1d([np.log10(x0), np.log10(x1)], [
                                 np.log10(y0), np.log10(y1)])

        # คำนวณ Sa_structure โดยใช้ฟังก์ชันการแก้ไขที่สร้างขึ้น และแปลงค่ากลับจาก log10 ด้วยการยกกำลังสิบ
        Sa_structure = 10**f([np.log10(T_structure)])[0]

    # plot function
    def response_spectrum_plot(T_data, S_data):  # ฟังก์ชันสร้างกราฟ
        fig = go.Figure()                         # สร้างกราฟ

        # main grapgh
        fig.add_trace(
            go.Scatter(
                x=T_data,
                y=S_data,
                mode='lines+markers',
                line=dict(color='blue', width=2,),
                showlegend=False,
                hoverinfo='skip',
            )
        )  # สร้างกราฟเส้น

        # T & Sa horizontal line
        fig.add_trace(
            go.Scatter(
                x=[min(T_data), T_structure],
                y=[Sa_structure, Sa_structure],
                mode='lines',  # 'lines+text'
                line=dict(dash='dash', width=3, color='red'),
                # text=[r'%.3f'%(Sa_structure), ''],
                # textfont=dict(color='red', size=16),
                # textposition="top right",
                hoverinfo='skip',
                showlegend=False,
            )
        )  # สร้างเส้นแนวนอน
        if bkk:  # ถ้าเป็นเขตพื้นที่กรุงเทพฯ
            # กำหนดค่า x เท่ากับ log10(T_data ที่น้อยที่สุด)
            x = np.log10(min(T_data))
            # กำหนดค่า y เท่ากับ log10(Sa_structure)
            y = np.log10(Sa_structure)
        else:
            x = min(T_data)  # กำหนดค่า x เท่ากับ T_data ที่น้อยที่สุด
            y = Sa_structure  # กำหนดค่า y เท่ากับ Sa_structure
        fig.add_annotation(  # สร้าง annotation บนกราฟ
            x=x, y=y,  # กำหนดตำแหน่ง x และ y
            text=r'%.3f' % (Sa_structure),  # กำหนดข้อความ
            xanchor="left",  # กำหนดตำแหน่งของข้อความ
            yanchor="bottom",  # กำหนดตำแหน่งของข้อความ
            font=dict(
                    color="red",
                    size=16
            ),  # กำหนดสีและขนาดของข้อความ
            showarrow=False,  # ไม่แสดงลูกศร
            # xshift=10,
        )

        # T & Sa vertical line
        fig.add_trace(
            go.Scatter(
                x=[T_structure, T_structure],
                y=[0.0, Sa_structure],
                mode='lines',  # 'lines+text'
                line=dict(dash='dash', width=3, color='red'),
                hoverinfo='skip',
                showlegend=False,
            )
        )  # สร้างเส้นแนวตั้ง
        if bkk:  # ถ้าเป็นเขตพื้นที่กรุงเทพฯ
            x = np.log10(T_structure)  # กำหนดค่า x เท่ากับ log10(T_structure)
            y = np.log10(0.01)  # กำหนดค่า y เท่ากับ log10(0.01)
        else:  # ถ้าไม่ใช่เขตพื้นที่กรุงเทพฯ
            x = T_structure  # กำหนดค่า x เท่ากับ T_structure
            y = 0.0  # กำหนดค่า y เท่ากับ 0
        fig.add_annotation(
            x=x, y=y,
            text=r'%.3f' % (T_structure),
            xanchor="left",
            yanchor="bottom",
            font=dict(
                    color="red",
                    size=16
            ),
            showarrow=False,
            # xshift=10,
        )  # สร้าง annotation บนกราฟ

        # T & Sa marker
        fig.add_trace(
            go.Scatter(
                x=[T_structure],
                y=[Sa_structure],
                mode='markers',
                marker=dict(color='red', size=8),
                showlegend=False,
                hoverinfo='skip',
            )
        )  # สร้าง marker บนกราฟ

        fig.update_layout(
            xaxis=dict(
                title='T (second)',
                fixedrange=True,
                range=[0.0, 2.0],
                rangemode="nonnegative",
                # dtick = 0.25,
            ),
            yaxis=dict(
                title='Sa (g)',
                fixedrange=True,
                range=[0.0, max(S_data)+0.05],
                scaleanchor="x", scaleratio=1,
                rangemode="nonnegative",
                # dtick = 0.2,
            ),
            margin=dict(t=20, b=40),
            height=300,
        )  # กำหนดรูปแบบกราฟ

        if bkk:  # ถ้าเป็นเขตพื้นที่กรุงเทพฯ
            # กำหนดขอบเขตแกน x และปรับให้เป็นลอการิทึม
            fig.update_xaxes(range=[np.log10(0.01), np.log10(10)], type="log")
            # กำหนดขอบเขตแกน y และปรับให้เป็นลอการิทึม
            fig.update_yaxes(range=[np.log10(0.01), np.log10(1)], type="log")

        return fig  # คืนค่ากราฟ

    col1, col2 = st.columns([0.7, 0.3])  # แบ่งคอลัมน์เป็นสองส่วน
    with col1:
        st.plotly_chart(response_spectrum_plot(T_data, S_data),
                        theme=None, use_container_width=True)  # แสดงกราฟ

        if structure == structure_list[0]:  # ถ้าโครงสร้างเป็นคอนกรีต
            st.write(
                r'Period of structure, $T = %.3f \mathrm{~sec}$' % (T_structure))
        else:  # ถ้าโครงสร้างเป็นเหล็ก
            st.write(
                r'Period of structure, $T = %.3f \mathrm{~sec}$' % (T_structure))

        st.write(
            r'Acceleration of structure, $S_a = %.3f \mathrm{~g}$' % (Sa_structure))

    with col2:  # แสดงข้อมูลในตาราง

        # คำนวณความยาวของข้อมูลที่น้อยที่สุด
        min_length = min(len(T_data), len(S_data))
        # กำหนดค่า T_data ให้มีความยาวเท่ากับ min_length
        T_data = T_data[:min_length]
        # กำหนดค่า S_data ให้มีความยาวเท่ากับ min_length
        S_data = S_data[:min_length]

        df = pd.DataFrame({
            'T (second)': T_data,
            'Sa (g)': S_data
        })  # สร้าง dataframe จากข้อมูล

        # แสดง dataframe
        st.dataframe(df, hide_index=True, use_container_width=True)

    st.write('### แรงเฉือนที่ฐานอาคาร, $V$')

    W = st.number_input(
        # รับค่าน้ำหนักโครงสร้าง
        label='น้ำหนักโครงสร้างประสิทธิผลของอาคาร, $W \mathrm{~[tonne]}$', min_value=0.0, value=500.0)

    st.write('**สัมประสิทธิ์ผลตอบสนองแรงแผ่นดินไหว**')
    Cs_ = Sa_structure*I/R  # คำนวณค่า Cs จากสมการ Cs = Sa_structure*I/R
    Cs = max(Cs_, 0.01)  # กำหนดค่า Cs ให้มีค่าไม่ต่ำกว่า 0.01

    st.markdown(
        r'$C_s = S_a \left( \frac{I}{R} \right) \qquad\qquad \ge \qquad 0.01$')
    st.markdown(r'$\quad\>\> = %.3f \left( \frac{%.2f}{%.2f} \right) \qquad\>\> \ge \qquad 0.01$' % (
        Sa_structure, I, R))
    st.markdown(r'$\quad\>\> = %.3f \qquad\qquad\quad \ge \qquad 0.01$' % (Cs_))
    st.markdown(r'$\quad\>\> = %.3f$' % (Cs))

    st.write('**แรงเฉือนที่ฐานอาคาร**')
    V = Cs*W
    st.markdown(r'$V = C_s W$')
    st.markdown(
        r'$\quad = %.3f \mathrm{~g} \times %.2f \mathrm{~tonne}$' % (Cs, W))
    st.markdown(r'$\quad = %.2f \mathrm{~tonne}$' % (V))

    st.write('### การกระจายแรงเฉือนที่ฐานเป็นแรงกระทำด้านข้าง')
    df_v_distribute = pd.DataFrame({
        'Floor': [4, 3, 2, 1],
        'Wi [tonne]': [125.0, 125.0, 125.0, 125.0],
        'Floor height [m]': [3.5, 3.5, 3.5, 3.5],
    })  # สร้าง dataframe จากข้อมูล

    st.write('**ค่าสัมประสิทธิ์กำหนดรูปแบบการกระจายแรง**')
    if T_structure <= 0.5:  # ถ้าค่า T น้อยกว่าหรือเท่ากับ 0.5
        k = 1.0            # กำหนดค่า k เท่ากับ 1.0
        st.write(r'สำหรับ $\qquad T \le 0.5 \mathrm{~sec}, \qquad k = 1.0$')
    elif T_structure >= 2.5:  # ถ้าค่า T มากกว่าหรือเท่ากับ 2.5
        k = 2.0           # กำหนดค่า k เท่ากับ 2.0
        st.write(r'สำหรับ $\qquad T \ge 2.5 \mathrm{~sec}, \qquad k = 2.0$')
    else:
        k = 1 + (T_structure-0.5)/2  # คำนวณค่า k จากสมการ k = 1 + (T-0.5)/2
        st.write(
            r'สำหรับ $\qquad 0.5 \mathrm{~sec} < T < 2.5 \mathrm{~sec}, \qquad k = 1+ \frac{T-0.5}{2} = 1+ \frac{%.2f-0.5}{2} = %.2f $' % (T_structure, k))

    st.write('**ตัวประกอบการกระจายแนวดิ่ง**')
    st.write(r'$C_{v i}=\frac{w_i h_i^k}{\sum_{i=1}^{n} w_i h_i^k}$')

    st.write(r'$F_i = C_{v i} V$')

    col1, col2 = st.columns(2)
    with col1:
        st.write('**Input** (this table is editable)')
        df_v_distribute = st.data_editor(
            df_v_distribute, num_rows="dynamic", key='df_v_distribute')  # แสดงตารางแก้ไขข้อมูล
    with col2:
        st.write('**Output**')
        df_v_cal = pd.DataFrame()
        df_v_cal['hi [m]'] = df_v_distribute.loc[::-
                                                 # คำนวณค่า hi จากข้อมูล
                                                 1, 'Floor height [m]'].cumsum()[::-1]
        wihik = df_v_distribute['Wi [tonne]'] * \
            (df_v_cal['hi [m]']**k)  # คำนวณค่า wihik จากข้อมูล
        df_v_cal['Cvi'] = wihik / wihik.sum()  # คำนวณค่า Cvi จากข้อมูล
        df_v_cal['Fi [tonne]'] = df_v_cal['Cvi']*V  # คำนวณค่า Fi จากข้อมูล
        # คำนวณค่า Vi จากข้อมูล
        df_v_cal['Vi [tonne]'] = df_v_cal['Fi [tonne]'].cumsum()

        st.dataframe(df_v_cal, hide_index=True)  # แสดง dataframe
