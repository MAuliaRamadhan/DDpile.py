import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d

#input file path
data = pd.read_csv('c:/ANYAAA/TEKNIK SIPIL/TDMRC/CPT titik/DATA SONDIR.csv') 

d = float(input('Diameter (m): '))
Safety_Factor_b = float(input('SF B : '))
Safety_Factor_a = float(input('SF S : '))

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

CPT (data, d, Safety_Factor_a, Safety_Factor_b)

