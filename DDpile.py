###########################################################################
# Program ini dapat digunakan secara terbuka

# Program ini dibuat untuk tujuan kegiatan MBKM LAB DRI, TDMRC USK 2023 
# oleh Mahasiswa S1-Teknik Sipil USK Angkatan 2020: 
# Anya Maghfirah 
# Feby Faradilla
# Humaira
# M. Aulia Ramadhan
# Maharani Qonita Jannah
# Tita Rachmanieta 
# Qamara Ramadhana

# Disclaimer!!!
# Kami tidak bertanggung jawab atas segala kerugian yang terjadi akibat dari penggunaan program ini
# Seluruh pengguna program ini dianggap telah membaca dan menyetujui pernyataan ini
###########################################################################

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math 
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d

#input file path
dt1_csv=pd.read_csv('C:/Users/ASUS TUF/Documents/Kampus/Smstr 6/Berkas MBKM/MBKM/Data Tanah 1.csv') 

#input diameter
d = float(input('Diameter (m): '))

#Input muka air tanah (mat)
mat = float(input('Muka air tanah (m):'))

#Input SF
SF_b = float(input('SF B :'))
SF_s = float(input('SF S :'))

#Input Metode berdasarkan data
Metode = input('Metode (CPT , NSPT_1, NSPT_2):') 

#Fungsi Luas lingkaran
def L_lingkaran (temp) :
   return math.pi*0.25*temp*temp

#Fungsi NSPT_1 (Reese & O'neil 1989)===============================================================================================================
def NSPT_1 (temp_data,temp_d,temp_mat,temp_SF_b,temp_SF_s):

   # Mencari Tanah Non-Kohesif #

   Ab = L_lingkaran (temp_d)                                                # Ab Luas permukaan ujung tiang

   Tebal=[0]                                                           # Mencari tebal setiap lapisan
   for x in range (1,len(temp_data.axes[0])): 
    Tebal.append(-(temp_data.Elevasi[x]-temp_data.Elevasi[x-1]))
   temp_data['Tebal']=Tebal

   temp_data['As']=temp_data['Tebal']*math.pi*d                            # As tebal selimut tiang tiap lapisan

   Tr=100                                                              # Tr teganga referensi 100 kpa

   temp_data['fb']=0.6*Tr*temp_data['SPT']                                 # Mencari fb 
   temp_data.loc[temp_data['fb'] > 4500, 'fb'] = 4500

   temp_data['Qb_s']=Ab*temp_data['fb']                                    # Mencari Qb Sand

   temp_data['Beta']=1.5-0.245*(-temp_data['Elevasi'])**0.5                # Mencari Beta
   for x in range (1,len(temp_data.axes[0])):                            # Koreksi nilai Beta untuk N < 15
      if temp_data.SPT[x] < 15 :
         temp_data.Beta[x] = (temp_data.SPT[x]/15)*temp_data.Beta[x]

   temp_data.loc[temp_data['Beta'] > 1.2, 'Beta'] = 1.2                    # 0.25 < Beta < 1.2 
   temp_data.loc[temp_data['Beta'] < 0.25, 'Beta'] = 0.25

   temp_data['BJ'] = 0
   for x in range (1,len(temp_data.axes[0])):                            # Berat jenis tanah
      if temp_data.Elevasi[x] > -temp_mat :
         temp_data.BJ[x] = 16
      else :
         temp_data.BJ[x] = 18

   temp_data['BJ_E'] = 0                                                  # Berat jenis efektif
   for x in range (1,len(temp_data.axes[0])):                            # Berat jenis tanah
      if temp_data.Elevasi[x] <= -mat :
         temp_data.BJ_E[x] = temp_data.BJ[x]-9.81
      else :
         temp_data.BJ_E[x] = temp_data.BJ[x]

   temp_data['Tekanan']=temp_data['Tebal']*temp_data['BJ_E']                   # Tekanan Satuan (Efektif, hapus '_E' untuk tegangan biasa)
   TK=[0]
   for x in range (1,len(temp_data.axes[0])):                            # Tekanan kumulatif
    TK.append(TK[x-1]+temp_data.Tekanan[x])
   temp_data['TK']=TK

   TO=[0]
   for x in range(1,len(temp_data.axes[0])):                             # Tekanan kumulatif di tengah lapisan
    TO.append(TK[x]-0.5*temp_data.Tekanan[x])
   temp_data['TO']=TO

   temp_data['fs']=temp_data['Beta']*temp_data['TO']                         # fs
   temp_data['Qs_s']=temp_data['fs']*temp_data['As']                         # Qs Sand


   # Mencari Tanah Kohesif

   Ap=Ab                                                               
   temp_data['Cu']=temp_data['SPT']*10*2/3

   Alfa = [0]
   for x in range(1,len(temp_data.axes[0])):
    if round(temp_data.Cu[x]/1000,1) <= 0.2 :
       Alfa.append(0.55)
    elif (round(temp_data.Cu[x]/1000,1) > 0.3 and round(temp_data.Cu[x]/1000) <= 0.4) :
       Alfa.append(0.42)
    elif (round(temp_data.Cu[x]/1000,1) > 0.4 and round(temp_data.Cu[x]/1000) <= 0.5) :
       Alfa.append(0.38)
    elif (round(temp_data.Cu[x]/1000,1) > 0.5 and round(temp_data.Cu[x]/1000) <= 0.6) :
       Alfa.append(0.35)
    elif (round(temp_data.Cu[x]/1000,1) > 0.6 and round(temp_data.Cu[x]/1000) <= 0.7) :
       Alfa.append(0.33)
    elif (round(temp_data.Cu[x]/1000,1) > 0.8 and round(temp_data.Cu[x]/1000) <= 0.9) :
       Alfa.append(0.31)
    else :
       Alfa.append(0.31)

   if d <= 0.5 :
      Nc = 9
   elif d > 0.5 and d <= 1 :
      Nc = 8
   else:
      Nc = 7

   temp_data['Qb_c']=Nc*temp_data['Cu']*Ap
   temp_data['Qs_c']=Alfa*temp_data['Cu']*temp_data['As']

   Qb=[0]
   for x in range(1,len(temp_data.axes[0])): 
    if temp_data.Jenis_Tanah[x] == 'Sand' :
       Qb.append(temp_data.Qb_s[x])
    else :
        Qb.append(temp_data.Qb_c[x])

   temp_data['Qb'] = Qb

   Qs=[0]
   for x in range(1,len(temp_data.axes[0])): 
    if temp_data.Jenis_Tanah[x] == 'Sand' :
       Qs.append(Qs[x-1]+temp_data.Qs_s[x])
    else :
        Qs.append(Qs[x-1]+temp_data.Qs_c[x])

   temp_data['Qs'] = Qs
   temp_data['Qu'] = temp_data['Qb_s']+temp_data['Qs']

   print(temp_data[['Qb','Qs','Qu']])

   temp_data['Qb_a']=temp_data['Qb']/temp_SF_b
   temp_data['Qs_a']=temp_data['Qs']/temp_SF_s

   temp_data['Q izin']= temp_data['Qb_a']+temp_data['Qs_a']
   print(temp_data[['Qb_a','Qs_a','Q izin']])

   y= temp_data['Elevasi']
   x1= temp_data['Qb']
   x2= temp_data['Qs']
   x3= temp_data['Qu']

   x6= temp_data['Q izin']

   fig, (ax1,ax2) = plt.subplots(1, 2, figsize = (10,5))

   ax1.plot(x1, y, label='Qb', color = 'green')
   ax1.plot(x2, y, label='Qs', color = 'blue')
   ax1.plot(x3, y, label='Qu', color = 'red')

   ax2.plot(x6, y, label=r'$Q_{all}$', color = 'black')

   fig.suptitle("Diagram Kapasitas N-SPT (Reese & O'neil 1989)")

   for ax in (ax1, ax2) :
      ax.set_xlabel('Kapasitas (kN)')
      ax.set_ylabel('Kedalaman (m)')
      ax.grid(True)
      ax.set_yticks(ticks=(temp_data.Elevasi))

   ax1.set_title('Daya Dukung Ultimit')
   ax2.set_title('Daya Dukung Izin')
   fig.legend()

   plt.show()

#Fungsi CPT (Schmertmann & Nottingham 1975)===============================================================================================================

def CPT (data, d, Safety_Factor_a, Safety_Factor_b):
    z = float(input('Panjang Pile (m) = '))

    #mencari Kuat Dukung Ultimit
    #Luas Penampang Tiang Ab


    def hitung_luas_lingkaran(d):
        radius = d / 2
        return math.pi * radius ** 2


    Ab = hitung_luas_lingkaran(d)

    # Luas Selimut Tiang As
    def hitung_luas_selimut(d,z):
        pi = math.pi
        keliling = pi * d * z
        return keliling

    As = hitung_luas_selimut(d,z)
    Elevasi = data['Elevasi']
    qc = data['qc']
    
    #Tahanan Ujung Satuan fb
    data_w = {
        'Kondisi Tanah': ['OCR=1', 'OCR=2-4', 'OCR=6-10'],
        'w': [1, 0.67, 0.5],
    }

    df = pd.DataFrame(data_w)
    print(df)
    w = float(input('w = '))

    #mencari nilai qc1 & qc2
    #qc1 kan dari 4D
    data_df=pd.DataFrame(data)
    rows_data_1 = data_df.iloc[0:16]
    selected_column = 'qc'
    column_data_1 = rows_data_1[selected_column]

    mean_qc1 = column_data_1.mean()

    rows_data_2 = data_df.iloc[17:23]
    selected_column = 'qc'
    column_data_2 = rows_data_2[selected_column]

    mean_qc2 = column_data_2.mean()

    qca = 0.5*(mean_qc1 + mean_qc2)

    fb = w*qca
    print("tahanan ujung satuan",fb)

    #mencari nilai daya dukung ujung Qb
    Qb = fb*Ab
    print("daya dukung ujung",Qb,'kPa')

    #Tahanan Gesek Satuan fs
    data_Kc = {
        'Kondisi Tanah': ['Tiang baja ujung bawah terbuka', 'Tiang pipa ujung bawah tertutup', 'Tiang beton'],
        'Kc': [0.008, 0.018, 0.012],
    }

    df = pd.DataFrame(data_Kc)
    print(df)
    Kc = float(input('Kc = '))

    fs = Kc*qc
    print("tahanan gesek satuan", fs)

    #daya dukung selimut tiang
    Qs = fs*As
    print("daya dukung selimut tiang",Qs)

    #Kuat Dukung Ultimit
    Qu = Qb+Qs
    print("Kuat Dukung Ultimit", Qu)

    #daya dukung izin
    Qa = Qu/Safety_Factor_a
    print("daya dukung ultimit izin",Qa)

    #Qb izin
    Qb_izin = Qb/Safety_Factor_b
    print("Tahanan ujung tiang izin", Qb_izin)

    data['Qs']=Qs
    data['Qu']=Qu
    data['Qb']=Qb
    data['Qball']=Qb_izin
    data['Qa']=Qa

    #Q, Qb dan Qa yang di plot
    index_to_plot = (data['Qu'] == z).idxmax()
    Quplot = data['Qu'][15:16]

    index_to_plot = (data['Qb'] == z).idxmax()
    Qbplot = data['Qb'][15:16]

    index_to_plot = (data['Qa'] == z).idxmax()
    Qaplot = data['Qa'][15:16]


    data['Qs']=Qs
    data['Quplot']=Quplot
    data['Qbplot']=Qbplot
    data['Qball']=Qb_izin
    data['Qaplot']=Qaplot
    print(data)

    y = data['Elevasi']
    x1 = data['Quplot']
    x2 = data['Qbplot']
    x3 = data['Qs'] 
    x4 = data['Qaplot'] 

   
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

    ax1.plot(x1, y, marker='o', markersize=5, label='Qu', color='purple')
    ax1.plot(x2, y, marker='o', markersize=5, label='Qb', color='blue')
    ax1.plot(x3, y, linewidth=2.5, label='Qs', color='green')
        
    ax2.plot(x4, y, marker='o', markersize=5, label='Qa', color='red')

    fig.suptitle(f'Diagram Kapasitas CPT')
    for ax in (ax1, ax2):
        ax.set_xlabel('Kapasitas (kN)')
        ax.set_ylabel('Kedalaman (m)')
        ax.grid(True)
        ax.set_yticks(ticks=(data.Elevasi))
    ax1.set_title('Kapasitas')
    ax2.set_title('Kapasitas Izin')
    fig.legend()

    plt.show()

#Fungsi NSPT_2 (Alpha Beta) ===============================================================================================================
def NSPT_2 (df, d, mat, SF_s, SF_b ): 
    Tebal = [0]                                                                         # Mencari tebal setiap lapisan
    for x in range (1, len(df.axes[0])):
        Tebal.append(-(df.Elevasi[x]-df.Elevasi[x-1]))
    df['Tebal'] = Tebal

    Ab = 1/4*math.pi*d**2                                                                  # Luas permukaan ujung tiang
    df['As']= df['Tebal']*math.pi*d                                                        # Luas selimut tiang tiap lapisan

    phi = [0]                                                                            # Mencari sudut friksi tanah
    for x in range (1, len(df.axes[0])):
        if (df.SPT[x] <= 4 ):
            phi.append(7*df.SPT[x])
        else:
            phi.append(27.12+(0.2857*df.SPT[x]))
    df['phi'] = phi

    # Tanah Kohesif #
    #Tahanan Kulit (Qs)
    Beta = [0]
    for x in range (1, len(df.axes[0])):
        Beta.append((1-math.sin(math.radians(df.phi[x])))*math.tan(math.radians(df.phi[x])))
    df['Beta'] = Beta

    df['BJ'] = 0                                                                      # Berat Jenis Tanah
    df['BJ_E'] = 0                                                                    # Berat Jenis Efektif
    for x in range (1, len(df.axes[0])):
        if (df.Elevasi[x] > -mat):
            df.BJ[x] = 16
        else:
            df.BJ[x] = 18
        if (df.Elevasi[x] <= -mat) :
            df.BJ_E[x] = df.BJ[x] - 9.81
        else:
            df.BJ_E[x] = df.BJ[x]

    df['Tekanan']= 0                                                                    # Tekanan Satuan 
    for x in range (1, len(df.axes[0])):
        if (df.Elevasi[x] > -mat):
            df.Tekanan[x] = df.BJ[x]*df.Tebal[x]
        else:
            df.Tekanan[x] = df.BJ_E[x]*df.Tebal[x]

    T_Kum = [0]                                                                          # Tekanan Kumulatif
    for x in range (1,len(df.axes[0])):                              
        T_Kum.append(T_Kum[x-1]+df.Tekanan[x])
    df['T_Kum']= T_Kum

    T0 = [0]                                                                             # Tekanan Kumulatif di tengah lapisan
    for x in range (1,len(df.axes[0])):
        T0.append(T_Kum[x]-0.5*df.Tekanan[x])
    df['T0']= T0

    df['Qsult_c'] = df['Beta'] * df['T0'] * df['As']

    #Tahanan Ujung (Qb)
    df['cu'] = (2/3)*df['SPT']*10                                                        # Mencari cu, cu dalam ton/m2 #ubah ke kN/m2

    if ( d <= 0.5):                        
        Nc = 9
    elif (0.5 < d <= 1):
        Nc = 7
    else:
        Nc = 6
    df['Nc'] = Nc

    df['Qbult_c'] = Nc * df['cu'] * Ab


    # Tanah Non-Kohesif #
    #Tahanan Kulit (Qs)

    fsult_s = [0]
    for x in range (1, len(df.axes[0])):
        if (df.SPT[x] <= 53):
            fsult_s.append(2.87*df.SPT[x])
        else:
            fsult_s.append((2.11*(df.SPT[x]-53))+ 148.7)
    df['fsult_s'] = fsult_s

    df['Qsult_s'] = df['fsult_s'] * df['As']

    #Tahanan Ujung (Qb)

    Qbult_s = [0]
    for x in range (1, len(df.axes[0])):
        Qbult_s.append(57.54*df.SPT[x]*Ab)
    df['Qbult_s'] = Qbult_s


    Qs = [0]
    for x in range (1,len(df.axes[0])):
        if df.Jenis_Tanah[x] == 'Sand':
            Qs.append(Qs[x-1]+df.Qsult_s[x])
        else :
            Qs.append(Qs[x-1]+df.Qsult_c[x])

    Qb = [0]
    for x in range (1,len(df.axes[0])):
        if df.Jenis_Tanah[x] == 'Sand':
            Qb.append(df.Qbult_s[x])
        else :
            Qb.append(df.Qbult_c[x])

    df['Qs'] = Qs
    df['Qb'] = Qb
    df['Qu'] = df['Qb'] + df['Qs']

    df['Qs ijin'] = df['Qs']/SF_s
    df['Qb ijin'] = df['Qb']/SF_b
    df['Qu ijin'] = df['Qb ijin'] + df ['Qs ijin']

    print(df[['Elevasi', 'SPT', 'Jenis_Tanah','Qsult_s','Qsult_c','Qs', 'Qb', 'Qu', 'Qs ijin', 'Qb ijin', 'Qu ijin']])

    # plot grafik
    y = df['Elevasi']
    x1 = df['Qb']
    x2 = df['Qs']
    x3 = df['Qu']
    x4 = df['Qu ijin']

    fig, (ax1,ax2) = plt.subplots(1, 2, figsize = (10,5))

    ax1.plot(x1, y, label = 'Qb', color = 'green')
    ax1.plot(x2, y, label = 'Qs', color = 'blue')
    ax1.plot(x3, y, label = 'Qu', color = 'red')

    ax2.plot(x4, y, label =r'$Q_{all}$', color = 'black')

    fig.suptitle('Diagram Kapasitas N-SPT (Alpha-Beta)')
    fig.supxlabel('Q (kN)')
    fig.supylabel('Kedalaman (m)')

    yticks = df.Elevasi
    for ax in (ax1, ax2):
        ax.grid(True)
        ax.set_yticks(yticks)
        ax.set_xlim(left = 0)
        ax.set_ylim(top = 0, bottom = -30)

    ax1.set_title('Daya Dukung Ultimit')
    ax2.set_title('Daya Dukung Izin')

    fig.legend()
    plt.show()



#MAIN=====================================================================================================
if Metode == 'NSPT_1':
   NSPT_1 (dt1_csv,d,mat,SF_b,SF_s)
elif Metode == 'CPT':
   CPT (dt1_csv, d, SF_b, SF_s)
else:
   NSPT_2 (dt1_csv, d, mat, SF_s, SF_b )
   

