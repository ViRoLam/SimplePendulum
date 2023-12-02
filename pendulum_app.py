############################################################################# Import des modules graphiques

import matplotlib.pyplot as plt #module graphique 
import matplotlib.patches as patches #module de création de patchs/cercles
import matplotlib.animation as animation #module d'animation
import numpy as np #module de calcul
from pendulum.pendulum_simulation_motion import *
#Pour augmenter la performance
import matplotlib as mpl
mpl.rcParams['path.simplify'] = True
mpl.rcParams['path.simplify_threshold'] = 1

#plt.rcParams.update({'figure.autolayout': True}) 

#Pour poser un style bien stylé, et optimiser un peu (on fait ce qu'on peut)
import matplotlib.style as mplstyle
mplstyle.use(['dark_background','fast'])

#Pour l'affichage de la fenêtre et des boutons (l'interface graphique quoi)
import tkinter as tk
from tkinter import Tk, Label, Entry, StringVar, Frame
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

COLOR1 = "#570ee8"
COLOR2 = "#d90b2d"

######################################################################## Animation 

#Fonctions pour gérer les couleurs, copiées sur stackoverflow
def hex_to_RGB(hex_str):
    """ #FFFFFF -> [255,255,255]"""
    return [int(hex_str[i:i+2], 16) for i in range(1,6,2)]

def get_color_gradient(c1, c2, n):
    """
    Given two hex colors, returns a color gradient
    with n colors.
    """
    assert n > 1
    c1_rgb = np.array(hex_to_RGB(c1))/255
    c2_rgb = np.array(hex_to_RGB(c2))/255
    mix_pcts = [x/(n-1) for x in range(n)]
    rgb_colors = [((1-mix)*c1_rgb + (mix*c2_rgb)) for mix in mix_pcts]
    return ["#" + "".join([format(int(round(val*255)), "02x") for val in item]) for item in rgb_colors]

def complementaryColor(my_hex):
    """Returns complementary RGB color

    Example:
    >>>complementaryColor('FFFFFF')
    '000000'
    """
    if my_hex[0] == '#':
        my_hex = my_hex[1:]
    rgb = (my_hex[0:2], my_hex[2:4], my_hex[4:6])
    comp = ['%02X' % (255 - int(a, 16)) for a in rgb]
    return ''.join(comp)
#---------------------------------------------------------------------------


#Non implémenté, car ne marche pas avec la manière dont les lignes sont dessinées sur matplotlib 
def f(x,n):
    if -n<x<n:
        return x
    else:
        return np.mod(x,n)
f = np.vectorize(f,otypes=[np.float])

def renormalize(x):
    return f((x+2*np.pi),(4*np.pi))-2*np.pi 
#---------------------------------------------------------------------------


#Fonctions de plots
def plot_all(d,omegas):
    '''
    fonction qui prend en argument un pendule avec des paramètres de simulation et qui dessine les plots
    return: fig, ax
    '''


    #On créé les couleurs qu'on va utiliser pour les différents pendules
    color1 = COLOR1
    color2 = COLOR2
    print(len(omegas))  
    if len(omegas) == 1:
        colors = [color1]
        
        colors_ep = [color2]
    else:
        colors = get_color_gradient(color1,color2,len(omegas))

        #Bon c'est un peu chiant mais on ajoute des couleurs pour distinguer l'énergie cénétique et potentielle
        #L'énergie potentielle est la couleur complémentaire de l'énergie cinétique
        colors_ep = get_color_gradient(complementaryColor(color1),complementaryColor(color2),len(omegas))

    fig, (ax_row1,ax_row2) = plt.subplots(2, 2)
    ax0,ax1 = ax_row1
    ax2,ax3 = ax_row2
    #print(root.winfo_width(),root.winfo_height())
    # On change la taille de la fenêtre (dans notre cas la fenêtre est dans un canvas, donc on change le canvas)
    fig.set_figwidth(15)
    fig.set_figheight(9)

    #On ajoute des titres aux axes
    ax0.set_title("Pendulum")
    ax1.set_title("Portrait de phase")
    ax2.set_title("Energie cinétique et potentielle")
    ax3.set_title("Vitesse angulaire")



    # On change l'aspect ratio du premier graphique, pour que le pendule ne soit pas écrasé
    ax0.set_box_aspect(1)

    #On définit les limites des axes

    #La limite du premier graphique est définie par la longueur du pendule (on se laisse un peu de marge d'où le +1)
    ax0.set_xlim(-d["length"]-d["mass"],d["length"]+d["mass"]) 
    ax0.set_ylim(-d["length"]-d["mass"],d["length"]+d["mass"]) 

    #La limite du deuxième graphique est définie par la vitesse_angulaire/theta maximal (on peut varier entre 2*pi et 4*pi pour le bonheur des yeux)
    ax1.set_xlim(-4*np.pi,4*np.pi)
    ax1.set_ylim(-4*np.pi,4*np.pi)

    #La limite du troisième graphique est définie par l'énergie cinétique/potentielle maximale, et le temps 
    ax2.set_xlim(d['debut'],d['fin'])
    
    ax2.set_ylim(0,max(np.max(ec_s),np.max(ep_s))) #on ajoute un peu de marge pour que les courbes ne soient pas collées au bord

    #La limite du quatrième graphique est définie par la vitesse maximale, et le temps
    ax3.set_xlim(d['debut'],d['fin'])
    ax3.set_ylim(-np.max(v_ang)-np.max(v_ang)/5,np.max(v_ang)+np.max(v_ang)/5) #on ajoute un peu de marge pour que les courbes ne soient pas collées au bord


    #On desactive les axes (pour un effet esthétique maximal)
    if not d['axes']:
        ax0.set_axis_off()
        ax1.set_axis_off()
        ax2.set_axis_off()
        ax3.set_axis_off()
    

    #Si l'utilisateur veut une grille, on l'ajoute ! 
    
    
    #Aller on peut commencer à dessiner

    # Ax0 : Pendule

    #on créer le cercle sur lequel le pendule est attaché 
    #on encapsule le cercle dans une double liste, pour que sa dimension soit homogène aux autres objets
    cercle_origine = [[patches.Circle((0, 0), 0.1, ec="none",color="black",zorder=10)]]
    ax0.add_artist(cercle_origine[0][0])


    #on créer les masse des pendules, qu'on va modéliser par des cercles
    circles = []
    for i,omega0 in enumerate(omegas):
        masse_x = np.cos(d["theta0"])*d["length"]
        masse_y = np.sin(d["theta0"])*d["length"]
        masse_cercle = patches.Circle((masse_x,masse_y), d["mass"], ec="none",color=colors[i])
        circles.append([masse_cercle])
        ax0.add_patch(masse_cercle)

  
    #on créer les lignes qui relient les cercles au pendule     
    pendulum_lines = []
    for i,omega0 in enumerate(omegas):
        line, = ax0.plot([], [], 'o-', lw=1,color=colors[i],alpha=1) 
        l = [line]
        # si le mode neon est activé, on ajoute des lignes de plus en plus épaisses et transparentes
        if d['neon']:
            for cont in range(3, 1, -1):
                line1, = ax0.plot([], [], 'o-', lw=cont, color=line.get_color(), zorder=5,
                    alpha=0.3)
                l.append(line1)
        pendulum_lines.append(l)


    # Ax1 : Portrait de phase

    #On créer les lignes de phases 
    phase_lines = []
    for i,omega0 in enumerate(omegas):
        phase_line, = ax1.plot([], [], '-', lw=2,color=colors[i],zorder=6)
        l = [phase_line]
        if d['neon']: #encore une fois si le mode neon est activé, on ajoute des lignes de plus en plus épaisses et transparentes
            for cont in range(6, 3, -1):
                phase_line1, = ax1.plot([],[], lw=2*cont, color=phase_line.get_color(), zorder=5,
                    alpha=0.15)
                l.append(phase_line1)
        phase_lines.append(l)

    #On créer les lignes de phases permanentes
    perm_phase_lines = []
    for i,omega0 in enumerate(omegas_perm):
        phase_line1, = ax1.plot([], [], '-', lw=1,color="grey",zorder=5,alpha=0.7)
        phase_line2, = ax1.plot([], [], '-', lw=1,color="grey",zorder=5,alpha=0.7)
        l = [phase_line,phase_line2]
        if d['neon']: #encore une fois si le mode neon est activé, on ajoute des lignes de plus en plus épaisses et transparentes
            for cont in range(6, 3, -1):
                phase_line1, = ax1.plot([],[], lw=cont, color=phase_line.get_color(), zorder=4,
                    alpha=0.1)
                phase_line2, = ax1.plot([],[], lw=cont, color=phase_line.get_color(), zorder=4,
                    alpha=0.1)
                l.append(phase_line1)
                l.append(phase_line2)
        perm_phase_lines.append(l)


    # Ax2 : Energie

    #On créer les courbes d'énergie cinétique et potentielle
    ec_lines = []
    ep_lines = []
    for i,omega0 in enumerate(omegas):
        ec_line, = ax2.plot([], [], '-', lw=1,color=colors[i],zorder=6)
        ep_line, = ax2.plot([], [], '-', lw=1,color=colors_ep[i],zorder=6)
        l_ec_lines = [ec_line]
        l_ep_lines = [ep_line]
        if d['neon']: #encore une fois si le mode neon est activé, on ajoute des lignes de plus en plus épaisses et transparentes
            for cont in range(6,2, -1):
                ec_line1, = ax2.plot([],[], lw=2*cont, color=ec_line.get_color(), zorder=5,
                    alpha=0.1)
                ep_line1, = ax2.plot([],[], lw=2*cont, color=ep_line.get_color(), zorder=5,
                    alpha=0.1)
                l_ec_lines.append(ec_line1)
                l_ep_lines.append(ep_line1)

        ec_lines.append(l_ec_lines)
        ep_lines.append(l_ep_lines)



    # Ax3 : Vitesse

    #on créer les courbes de vitesse angulaire
    v_lines = []
    for i,omega0 in enumerate(omegas):
        v_line, = ax3.plot([], [], '-', lw=1,color=colors[i],zorder=6)
        l = [v_line]
        if d['neon']:
            for cont in range(6,2, -1):
                v_line1, = ax3.plot([],[], lw=2*cont, color=v_line.get_color(), zorder=5,
                    alpha=0.1)
                l.append(v_line1)
        v_lines.append(l)
    

    #On ajuste la taille des subplots pour que l'écran soit rempli
    fig.tight_layout()
    #fig.subplots_adjust(hspace=0, wspace=0), en commentaire car ça ne change rien

    return fig,ax0,ax1,ax2,ax3,cercle_origine,pendulum_lines,circles,phase_lines,perm_phase_lines,ec_lines,ep_lines,v_lines


#---------------------------------------------------------------------------

#Fonctions utilitaires, pour gérer les listes de listes
def flatten(l):
    return [item for sublist in l for item in sublist]


def concatenate_and_flatten(l):
    return flatten([flatten(item) for item in l])

def concatenate(l1,l2):
    return [item for sublist in [l1,l2] for item in sublist]
#---------------------------------------------------------------------------

#Fonction d'initialisation
def init_all():
    #On initialise les lignes
    for line in pendulum_lines:
        for i in range(len(line)):
            line[i].set_data([], [])

    for line in phase_lines:
        for i in range(len(line)):
            line[i].set_data([], [])
    
    for line in perm_phase_lines:
        for i in range(len(line)):
            line[i].set_data([], [])

    for line in ec_lines:
        for i in range(len(line)):
            line[i].set_data([], [])

    for line in ep_lines:
        for i in range(len(line)):
            line[i].set_data([], [])
    
    for line in v_lines:
        for i in range(len(line)):
            line[i].set_data([], [])

    #On initialise les cercles
    #Pas implémenté pour l'instant, mais on peut le faire si on veut, mais jsp si c'est utile
    
    return concatenate_and_flatten([cercle_origine,pendulum_lines,circles,phase_lines,perm_phase_lines,ec_lines,ep_lines,v_lines])

#Fonction d'animation
def animate_all(i):
    global paused, retard, started,just_started

    line_length = d['line_length']
    if just_started:
        retard = i
        just_started = False
        return init_all()
        
    #print("started:",started)
    #print("paused:",paused)
    if paused:
        retard += 1 #on ajoute du retard à l'animation pendant quelle est en pause, si on ne le fait pas l'animation "saute" quand on la réactive 
        return concatenate_and_flatten([cercle_origine,pendulum_lines,circles,phase_lines,perm_phase_lines,ec_lines,ep_lines,v_lines])
    

    i -= retard #on retire le retard à la frame actuelle
    frames = len(sols[0][:,0])

    #d'ailleurs, remarquez qu'on écrit jamais sols[i], mais toujours avec un modulo (le nombre de frames)
    #comme ça, l'animation peut "tourner" en boucle 

    #Bon on commence à dessiner, là ça devient sérieux 
    #on commence par les lignes de phases permanentes
    '''
    for j in range(len(perm_phase_lines)):
        for k in range(len(perm_phase_lines[0])):
            if j % 2== 0:
                perm_phase_lines[j][k].set_data(sols_perm[j][:, 0],sols_perm[j][:, 1])
            else:
                perm_phase_lines[j][k].set_data(-sols_perm[j-1][:,0],sols_perm[j-1][:, 1])
    '''
    #puis on fait le reste
    for j in range(len(omegas)):
        # Ax0: le pendule 

        #On définit/calcule les coordonnées du pendule
        x1 = d['length']*np.sin(sols[j][:, 0])
        y1 = -d['length']*np.cos(sols[j][:, 0])
        
        #On dessine les lignes
        #Notez que le -p, permet de créer un effet de trainée
        for p in range(len(pendulum_lines[j])):
            thisx = [0, x1[(i-p)%frames]]
            thisy = [0, y1[(i-p)%frames]]
            pendulum_lines[j][p].set_data(thisx, thisy)
        
        #On dessine les cercles, on s'en fiche un peu pour être honnête
        circles[j][0].set_center((x1[i%frames],y1[i%frames]))

        #Ax1: le portrait de phase

        #On dessine les lignes du portrait de phase 
        for k in range(len(phase_lines[0])):
            phase_lines[j][k].set_data(sols[j][(i-line_length-k)%frames:i%frames, 0],sols[j][(i-line_length-k)%frames:i%frames, 1])
        
        
        #Ax2: l'énergie

        #On dessine les courbes d'énergie cinétique et potentielle
        
        for k in range(len(ec_lines[0])):
            ec_lines[j][k].set_data(t[0:i%frames],ec_s[j][0:i%frames])
            ep_lines[j][k].set_data(t[0:i%frames],ep_s[j][0:i%frames]) #(i-line_length-k)%frames

        #Ax3: la vitesse
        for k in range(len(v_lines[0])):
            v_lines[j][k].set_data(t[0:i%frames],v_angs[j][0:i%frames])

    return concatenate_and_flatten([cercle_origine,pendulum_lines,circles,phase_lines,perm_phase_lines,ec_lines,ep_lines,v_lines])
#---------------------------------------------------------------------------

def run_calculations():
    global frame,root,canvas,d,omegas,paused,started,sols_perm,sols,thetas,v_angs,ec_s,ep_s,nb_pend_str,grav_str,borne0_str,borne1_str,temps_str,frottement_str,axes_int,neon_int,fig,ax0,ax1,ax2,ax3,cercle_origine,pendulum_lines,circles,phase_lines,perm_phase_lines,ec_lines,ep_lines,v_lines,canvas,anim,retard,just_started #on utilise des variables globales, pour pouvoir les réutiliser plus tard
    sols = []
    thetas = []
    v_angs = []
    ec_s = []
    ep_s = []

    
    if int(nb_pend_str.get()) <= 1:
        omegas =[int(borne0_str.get())]
    else:
        omegas = np.linspace(int(borne0_str.get()),int(borne1_str.get()),int(nb_pend_str.get()))
    for omega0 in omegas:
        #print(f"Doing {omega0}")
        d = initiate_simulation(length=1,mass=0.1,theta0=0,omega0=omega0,nb_points = int(temps_str.get())*20,fin=int(temps_str.get()),g=float(grav_str.get()),lbd=float(frottement_str.get()),neon=bool(neon_int.get()),axes=bool(axes_int.get()))

        t, sol = find_solution(d)
        sols.append(sol)

        theta, v_ang = sol[:,0], sol[:,1]
        thetas.append(theta)
        v_angs.append(v_ang)

        ec,ep = find_energie(sol,d)
        ec_s.append(ec)
        ep_s.append(ep)

    #On crée les plots, et on récupère les objets qui nous intéressent
    
    #frame.destroy()
    #frame = Frame(root)
    #frame.grid(row=3,column=0,columnspan=11)
    for widget in frame.winfo_children():
        widget.destroy()
    #canvas.destroy()
    fig,ax0,ax1,ax2,ax3,cercle_origine,pendulum_lines,circles,phase_lines,perm_phase_lines,ec_lines,ep_lines,v_lines = plot_all(d,omegas)
    
    #On crée le canvas dans lequel on va afficher les plots
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack()#grid(row=3,column=0,columnspan=11)#.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)


    #On execute l'animation
    anim = animation.FuncAnimation(fig, animate_all, init_func=init_all,frames=len(t), interval=1,blit=True) 
    #fig,ax0,ax1,ax2,ax3,cercle_origine,pendulum_lines,circles,phase_lines,ec_lines,ep_lines,v_lines = update_all(d,omegas,fig,ax0,ax1,ax2,ax3,ec_s,ep_s,v_angs)
    #init_all()

    
    paused = False
    started = True
    just_started = True
   
    #anim.save('pendulum.gif', writer='imagemagick', fps=60)


def start():
    global paused,started,button_start
    #button_pause.configure(text="Pause")
    run_calculations()

#Fonction pour mettre en pause/démarrer l'animation 
def pause():
    global paused, retard, button_pause, started 
    if started:
        if paused:
            button_pause.configure(text="Pause")
        else:
            button_pause.configure(text="Resume")
        paused = not paused


#Bon ça rigole plus, on commence à EXECUTER
if __name__ == "__main__":

    #On définit des variables globales, qui vont être utiles à la simulation
    paused = True
    retard = 0
    started = False
    just_started = True
    
    #On crée la fenêtre
    root = tk.Tk()

    #On la met en plein écran
    root.attributes("-fullscreen", True)

    #On lui ajoute un titre (pas très utile puisque la fenêtre est en plein écran, mais on sait jamais)
    root.title("Pendulum")

    #On change la couleur de fond
    root.configure(bg='black')

    # Cursor 
    root.config(cursor="dot") 

    #On définit la grille
    #root.columnconfigure(0,weight=0.5)
    root.rowconfigure(3,weight=9)

    #On calcule les solutions au problème (au préalable)
    sols = []
    thetas = []
    v_angs = []
    ec_s = []
    ep_s = []
    
    omegas = np.linspace(0,6,20)
    for omega0 in omegas:
        #print(f"Doing {omega0}")
        d = initiate_simulation(1,0.03,0,omega0,nb_points = 200,fin=10)

        t, sol = find_solution(d)
        sols.append(sol)

        theta, v_ang = sol[:,0], sol[:,1]
        thetas.append(theta)
        v_angs.append(v_ang)

        ec,ep = find_energie(sol,d)
        ec_s.append(ec)
        ep_s.append(ep)

    sols_perm = []
    omegas_perm = np.linspace(-12,12,20)
    for omega0 in omegas_perm:
        d = initiate_simulation(1,0.03,0,omega0,nb_points = 200,fin=10,lbd=0)

        t, sol = find_solution(d)
        sols_perm.append(sol) 
    
    #On modifie la taille de la fenêtre
    root.geometry("1440x900")
    root.resizable(False, False)
    

    #On ajoute le reste de l'interface graphique

    LabelSettings = {'font':("Arial", 20),'bg':"Black",'fg':"ghostwhite",'padx':5, 'pady':5}

    #textBox.insert(0, "This is the default text") 

    #nombre de pendules
    label_str_nb_pend=StringVar()
    label_str_nb_pend.set("Nombre de pendules")
    label_nb_pend=Label(root, textvariable=label_str_nb_pend)
    label_nb_pend.grid(row=0,column=0 )
    label_nb_pend.config(**LabelSettings)
    
    nb_pend_str=StringVar()
    nb_pend_str.set("6")
    entry_nb_pend=Entry(root,textvariable=nb_pend_str,width=5,bg="white",fg="black",bd=0)
    entry_nb_pend.grid(row=0,column=1)

    #gravité
    label__str_grav=StringVar()
    label__str_grav.set("Gravité")
    label_grav=Label(root, textvariable=label__str_grav)
    label_grav.grid(row=1,column=0 )
    label_grav.config(**LabelSettings)
    
    grav_str=StringVar()
    grav_str.set("9.8")
    entry_grav=Entry(root,textvariable=grav_str,width=5,bd=0)
    entry_grav.grid(row=1,column=1 )

    #borne_min_omega0
    label__str_borne0=StringVar()
    label__str_borne0.set("Borne min")
    label_borne0=Label(root, textvariable=label__str_borne0)
    label_borne0.grid(row=0,column=2 )
    label_borne0.config(**LabelSettings)
    
    borne0_str=StringVar()
    borne0_str.set("-5")
    entry_borne0=Entry(root,textvariable=borne0_str,width=5,bd=0)
    entry_borne0.grid(row=0,column=3 )

    #borne_max_omega0
    label__str_borne1=StringVar()
    label__str_borne1.set("Borne max")
    label_borne1=Label(root, textvariable=label__str_borne1)
    label_borne1.grid(row=1,column=2 )
    label_borne1.config(**LabelSettings)
    
    borne1_str=StringVar()
    borne1_str.set("6")
    entry_borne1=Entry(root,textvariable=borne1_str,width=5,bd=0)
    entry_borne1.grid(row=1,column=3 )


    #temps
    label__str_temps=StringVar()
    label__str_temps.set("Durée")
    label_temps=Label(root, textvariable=label__str_temps)
    label_temps.grid(row=0,column=5 )
    label_temps.config(**LabelSettings)
    
    temps_str=StringVar()
    temps_str.set("10")
    entry_temps=Entry(root,textvariable=temps_str,width=5,bd=0)
    entry_temps.grid(row=0,column=6 )

    #frottement
    label__str_frottement=StringVar()
    label__str_frottement.set("Frottement")
    label_frottement=Label(root, textvariable=label__str_frottement)
    label_frottement.grid(row=1,column=5 )
    label_frottement.config(**LabelSettings)
    
    frottement_str=StringVar()
    frottement_str.set("0.05")
    entry_frottement=Entry(root,textvariable=frottement_str,width=5,bd=0)
    entry_frottement.grid(row=1,column=6 )

    #grille
    axes_int = tk.IntVar()
    checkbutton_grille = tk.Checkbutton(root, text='axes',variable=axes_int, onvalue=1, offvalue=0)
    checkbutton_grille.config(**LabelSettings)
    checkbutton_grille.grid(row=0,column=8 )
    #néon
    neon_int = tk.IntVar()
    checkbutton_neon = tk.Checkbutton(root, text='neon',variable=neon_int, onvalue=1, offvalue=0)
    checkbutton_neon.config(**LabelSettings)
    checkbutton_neon.grid(row=1,column=8 )
    
    button_start = tk.Button(master=root, text="Start", command=start,width=10,bg='red',bd=0,height=2)
    button_start.grid(row=0,column=9 )#.pack(side=tk.TOP)

    button_pause = tk.Button(master=root, text="Pause", command=pause,width=10,bd=0,height=2)
    button_pause.grid(row=1,column=9 )#.pack(side=tk.TOP)

    
    d = initiate_simulation(length=1,mass=0.1,theta0=0,omega0=0,nb_points = 200,fin=int(temps_str.get()),g=float(grav_str.get()),lbd=float(frottement_str.get()),neon=bool(neon_int.get()),axes=bool(axes_int.get()))

    #On crée les plots, et on récupère les objets qui nous intéressent
    fig,ax0,ax1,ax2,ax3,cercle_origine,pendulum_lines,circles,phase_lines,perm_phase_lines,ec_lines,ep_lines,v_lines = plot_all(d,omegas)
    frame = Frame(root,bg="black")
    frame.grid(row=3,column=0,columnspan=11)
    #On crée le canvas dans lequel on va afficher les plots
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack()#grid(row=3,column=0,columnspan=11)#.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)


    #On execute l'animation
    anim = animation.FuncAnimation(fig, animate_all, init_func=init_all,frames=range(1, len(sols[0])), interval=(d['fin']-d['debut'])*d['nb_points'],blit=True) 
    #anim.save('pendulum.gif', writer='imagemagick', fps=60)
    #On lance enfin la boucle principale de l'interface graphique
    tk.mainloop()
