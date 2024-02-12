import random as rd
import csv
from tqdm import tqdm


def thegame():
  print("Bienvenue sur l'interface de Defensio. Je suis Ran, votre assistant presque magique. \n")

  #Intro
  print("Vous êtes trois par équipe, chaque persone doit choisir un rôle et à chacun des rôles sera attribué une jauge de responsabilité.")
  print("Je vous laisse choisir vos rôles puis découvrir vos personnages. \n")
  #Phase 0 de tutoriel avec des cartes prédéfinies
  print("La phase 0, le tutoriel, peut commencer.")
  print("Dans les différentes phases, vous serez amenés à manipuler des cartes ou des jetons, je vous guiderai tout le long, ne vous inquiétez pas.")
  print("Piochons quelques cartes pour voir à quoi elles ressemblent. Dire oui ou non influencera vos jauges.")
  #cartes tuto
  tuto_carte1 = ['Engager un centralien, euh je veux dire un comédien pour amuser la foule sur la place du marché', 0, 5, -5, 0, 0, 0]
  tuto_carte2 = ['Inviter les voisins au BarBu', 5, 5, -5, 0, -5, 5]
  tuto_carte3 = ['Planter des arbres', 0, 2, -2, -2, 0, 2]
  tuto_cartes = [tuto_carte1, tuto_carte2, tuto_carte3]
  #début tuto
  for j in range(3):
    for i, carte in enumerate(tuto_cartes):
        print(f"Voici la carte numéro {i} \n")
        print("Voulez-vous : " +carte[0] +"\n")
        print("Effet sur la popularité :", carte[1])
        print("Effet sur les relations :", carte[2])
        print("Effet sur les finances :", carte[3])

        choix = input("Oui ou non ? ")
        if choix.lower() == "oui":
            oC = int(carte[1])
            oR = int(carte[2])
            oI = int(carte[3])
            popularite += oC
            relations += oR
            finances += oI
        elif choix.lower() == "non":
            nC = int(carte[4])
            nR = int(carte[5])
            nI = int(carte[6])
            popularite += nC
            relations += nR
            finances += nI

        print("\n Popularité", popularite, "Relations", relations, "Finances", finances, "\n")
      

  popularite = 50
  relations = 50
  finances = 50
  defenses = {"feu" : 0, "terre" : 0, "eau" : 0, "air" : 0}

  print("Voici les valeurs de vos 3 jauges :", "Popularité", popularite, "Relations", relations, "Finances", finances, "\n")
  print("Comme vous avez pu le voir, vous pouvez aussi construire des défenses pour vous protéger des éléments. Elles sont précieuses, ne les oubliez pas.")
  print("Mais, attention, si une de vos barres passe dans le négatif, vous serez forcés de prendre le choix qui vous sort de cette situation.")

  #ils positionnent leurs châteaux et remplissent leurs tableau de prévention
  print("Je vous laisse positionner votre château à présent et remplir votre tableau de prévention stratégique. Soyez intelligents et réfléchis.")
  #chaque carte dans cartes est un dictionnaire avec les clés ['Choix', 'Oui R', 'Oui C', 'Oui I ', 'Non R', 'Non C ', 'Non I ', 'feu', 'terre', 'eau', 'air', 'intro', 'outro', '', 'index']

  #phase 1
  print("La phase 1 peut à présent commencer !")

  cartes = []
  with open("./static/cartes_action.tsv", "r", newline = "") as mycsv:
    reader = csv.DictReader(mycsv, delimiter = "\t")
    for idx, row in enumerate(reader):
      if row['Oui R']=='':
        break
      row['index'] = idx
      cartes.append(row)

  rd.shuffle(cartes)
  continuer = True

  while continuer == True:
      for i, carte in enumerate(cartes):
          print(f"Voici la carte numéro {i + 1} \n")
          print("Voulez-vous : " +carte["Choix"] +"\n")
          print("Effet sur la popularité :", carte["Oui C"])
          print("Effet sur les relations :", carte["Oui R"])
          print("Effet sur les finances :", carte["Oui I "])

          magnet = ''
          temp = [(0, 'feu'), (0, 'terre'), (0, 'eau'), (0, 'air')]
          for i, defense in enumerate(temp):
            if carte[defense[1]]!='':
              magnet+= '+ 1 défense ' + defense[1]
              temp[i]=(int(carte[defense[1]]), temp[i][1])
          if magnet!='':
            print(magnet)


          choix = input("Oui ou non ? ")
          peutAccepter = True
          peutRefuser = True
          if choix.lower() == "oui":
              oC = int(carte["Oui C"])
              oR = int(carte["Oui R"])
              oI = int(carte["Oui I "])
              if (popularite+oC<0) or (relations+oR<0) or (finances+oI<0):
                print("Vous ne pouvez pas accepter cela.")
                choix = "non"
                peutAccepter = False
                break
              popularite += oC
              relations += oR
              finances += oI
              if magnet!='':
                for i, elt in enumerate(temp):
                  if elt[0]>0:
                    defenses[elt[1]]+=elt[0]

          elif choix.lower() == "non":
              nC = int(carte["Non C "])
              nR = int(carte["Non R"])
              nI = int(carte["Non I "])
              if (popularite+nC<0) or (relations+nR<0) or (finances+nI<0):
                print("Vous ne pouvez pas refuser cela.")
                peutRefuser = False
                break
              popularite += nC
              relations += nR
              finances += nI
          else:
            if peutRefuser == False:
              break
            else:
              choix = input("Oui ou non ? ")

          print("\n Popularité", popularite, "Relations", relations, "Finances", finances, "\n")
          print("Réserve : " + str(defenses["feu"]) + " défenses feu, " +str(defenses["terre"])+ " défenses terre, " +str(defenses["eau"])+ " défenses eau, " +str(defenses["air"])+ " défenses air.\n")

          while continuer:
            try:
              continuer = bool(int(input("Veux-tu continuer à tirer des cartes ? 1 pour oui et 0 pour non ? ")))
              break
            except:
              None

          if not continuer:
              break