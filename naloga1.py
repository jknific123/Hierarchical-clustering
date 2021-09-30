import csv
import math


def match(ime_trenutne_drzave, seznam):  # funkcija preverja ce v list drzav se nismo dodali trenutne drzave

    for x in seznam:
        if ime_trenutne_drzave == x:
            return True

    return False


def read_file(file_name):
    """
    Read and process data to be used for clustering.
    :param file_name: name of the file containing the data
    :return: dictionary with element names as keys and feature vectors as values
    """
    counter = 0
    stDrzav = 0
    seznam = []  # seznam vseh drzav
    slovar = {}  # slovar vseh drzav
    f = open("eurovision-finals-1975-2019.csv", "rt", encoding="utf8")

    for line in csv.reader(f):

        ime_trenutne_drzave = line[2]
        if counter != 0:
            if not match(ime_trenutne_drzave, seznam):  # ce drzave se ni v seznamu jo dodamo
                seznam.append(ime_trenutne_drzave)
                # print(ime_trenutne_drzave + "\n")  # izpis za testiranje
                stDrzav += 1

        counter += 1

    f.seek(0)  # prestavimo se na zacetek datoteke
    counter = 0

    # ustvarimo potreben slovar slovarjev
    slovar_stevila_glasov = {}
    for x in seznam:
        slovar[x] = {}
        slovar_stevila_glasov[x] = {}
    # slovar slovarejv napolnimo z zacetnimi vrednostmi
    for x in seznam:
        for y in seznam:
            slovar[x][y] = 0
            slovar_stevila_glasov[x][y] = 0
    # print(slovar)

    # gremo drugic cez datoteko in naredimo sestevanje glasov po letih
    for line in csv.reader(f):

        if counter != 0:
            drzava_from = line[2]
            drzava_to = line[3]
            tocke = line[4]
            trenutne = slovar[drzava_from][drzava_to]
            slovar[drzava_from][drzava_to] = trenutne + int(tocke)
            trenutno_stevilo = slovar_stevila_glasov[drzava_from][drzava_to]
            slovar_stevila_glasov[drzava_from][drzava_to] = trenutno_stevilo + 1

        counter += 1

    f.close()
    # print(slovar)

    # normalizacija podatkov
    for x in slovar:
        for y in slovar:
            trenutne = slovar[x][y]
            glasovi = slovar_stevila_glasov[x][y]
            if glasovi != 0:
                slovar[x][y] = trenutne / glasovi
            else:
                slovar[x][y] = -1

    #  print(slovar["Belgium"])
    return slovar


class HierarchicalClustering:
    def __init__(self, data):
        """Initialize the clustering"""
        self.data = data
        # self.clusters stores current clustering. It starts as a list of lists
        # of single elements, but then evolves into clusterings of the type
        # [[["Albert"], [["Branka"], ["Cene"]]], [["Nika"], ["Polona"]]]
        self.clusters = [[name] for name in self.data.keys()]

    def row_distance(self, r1, r2):
        """
        Distance between two rows.
        Implement either Euclidean or Manhattan distance.
        Example call: self.row_distance("Polona", "Rajko")

        d = zip(self.data["Albania"], self.data["Armenia"])

        for a, b in d:
            print(a, b)

        """

        keys = list(self.data)
        prvi = keys[0]
        secondKeys = list(self.data[prvi])

        # ce je testni primer izracunamo po tej formuli
        if (type(self.data[prvi]) is list):
            return math.sqrt(sum((a - b) ** 2 for a, b in zip(self.data[r1], self.data[r2])))
        # ce pa je datoteka evrovision izracunamo po tej formuli
        else:

            # print(list(self.data)[0])

            pari = zip(self.data[r1], self.data[r2])

            sestevek = 0
            stManjkajocih = 0
            for a, b in pari:

                if not (self.data[r1][a] == -1 or self.data[r2][b] == -1):
                    sestevek += (self.data[r1][a] - self.data[r2][b]) ** 2
                else:
                    stManjkajocih += 1

            # sestevek += (((53 / stManjkajocih)) * sestevek)

            return math.sqrt(sestevek)

    # metoda toList nam clusterje (list listov) spremeni v en list ter tako omogoci lazje racunanje razdalj
    def toList(self, seznam):
        if len(seznam) == 2:
            return self.toList(seznam[0]) + self.toList(seznam[1])
        else:
            return seznam

    def povprecniVektor(self, cluster):

        listDrzav = self.data.keys()

        dolzinaClusterja = len(cluster)
        print(dolzinaClusterja)
        slovar = {}

        for x in listDrzav:
            slovar[x] = 0

        #sestejemo
        for x in cluster:  # po listu cluster
            for y in self.data:  # po slovarju podatkov
                if (self.data[x][y] != -1):
                    slovar[y] += self.data[x][y]
                else :
                    slovar[y] += 0

        sortSlovar1 = sorted(slovar.items(), key=lambda x: x[1], reverse=True)

        # povprecimo
        for a in slovar:
            slovar[a] = slovar[a] / dolzinaClusterja

        # print(slovar)

        sortSlovar = sorted(slovar.items(), key=lambda x: x[1], reverse=True)

    def cluster_distance(self, c1, c2):
        """
        Compute distance between two clusters.
        Implement either single, complete, or average linkage.
        Example call: self.cluster_distance(
            [[["Albert"], ["Branka"]], ["Cene"]],
            [["Nika"], ["Polona"]])

        Uporabimo razdaljo average linkage med clousterji

        average linkage:

        cluster1 = self.toList(c1)
        cluster2 = self.toList(c2)

        razdalja = 0
        for x in cluster1:
            for y in cluster2:
                razdalja += self.row_distance(x, y)

        rezultat = razdalja / (len(cluster1) * len(cluster2))
        """

        # med clusterji uporabimo razdaljo complete-linkage
        cluster1 = self.toList(c1)
        cluster2 = self.toList(c2)

        max = -92233720368547758
        razdalja = 0
        for x in cluster1:
            for y in cluster2:
                razdalja = self.row_distance(x, y)
                if (razdalja > max):
                    max = razdalja

        rezultat = max

        return rezultat

    def closest_clusters(self):
        """
        Find a pair of closest clusters and returns the pair of clusters and
        their distance.

        Example call: self.closest_clusters(self.clusters)
        """
        # s standardnim iskanjem minimuma poiscemo najkrajso razdaljo med clusterji
        par = {}
        min = 92233720368547758
        for x in self.clusters:
            for y in self.clusters:
                if x != y:
                    razdalja = self.cluster_distance(x, y)
                    if razdalja < min:
                        min = razdalja
                        par[0] = x
                        par[1] = y
                        par[2] = min

        # vrnemo slovar ki vsebuje cluster x cluster y in njuno razdaljo
        return par

    def run(self):
        """
        Given the data in self.data, performs hierarchical clustering.
        Can use a while loop, iteratively modify self.clusters and store
        information on which clusters were merged and what was the distance.
        Store this later information into a suitable structure to be used
        for plotting of the hierarchical clustering.
        """

        while (len(self.clusters) > 2):
            # pridobimo par clusterjev med katerima je najkrajsa razdalja
            par = self.closest_clusters()
            # print(par)

            # spremenimo self.clusters tako da ne vsebuje vec posameznih clusterjev iz para ki ga returnamo iz closest_clusters
            self.clusters = [c for c in self.clusters if c not in (par[0], par[1])]

            # spremenjenemu seznamu self.clusters nato dodamo nov element in sicer seznam ki ga pridobimo z zdruzitvijo clusterjev iz par-a
            self.clusters.append([par[0], par[1]])



    # pomozna funkcija za printanje presledkov
    def printajPresledke(self, stPresledkov):
        for x in range(stPresledkov):
            print(" ", end="")

    # rekurzivna funkcija za izpis dendrograma
    def dendrogram(self, clusters, stPresledkov):

        # rekurzivno pomikanje v globino
        if len(clusters) == 2:
            self.dendrogram(clusters[0], stPresledkov + 4)
            self.printajPresledke(stPresledkov)
            print("----|")
            self.dendrogram(clusters[1], stPresledkov + 4)
        # izpis ce je samo se en element v clusterju
        else:
            self.printajPresledke(stPresledkov)
            print("----", clusters[0])

    def plot_tree(self):
        """
        Use cluster information to plot an ASCII representation of the cluster
        tree.
        """
        print()
        print()
        self.dendrogram(self.clusters, 0)


if __name__ == "__main__":
    DATA_FILE = "eurovision-finals-1975-2019.csv"
    hc = HierarchicalClustering(read_file(DATA_FILE))

    skupina0 = ["Belgium"]
    skupina1 = ["Austria", "Switzerland", "Yugoslavia", "Bosnia & Herzegovina", "Croatia", "Slovenia"]
    skupina2 = ["Albania", "Serbia", "Serbia & Montenegro", "F.Y.R. Macedonia", "Montenegro"]
    skupina3 = ["Armenia"]
    skupina4 = ["Moldova", "Georgia", "Russia", "Ukraine", "Belarus", "Azerbaijan", "Turkey", "Morocco"]
    skupina5 = ["Greece", "Cyprus", "Romania", "Bulgaria", "Italy", "North Macedonia", "Czech Republic", "Malta",
                "San Marino"]
    skupina6 = ["Andorra"]
    skupina7 = ["Lithuania", "Estonia", "Latvia", "Australia", "Finland", "Sweden", "Denmark", "Norway", "Iceland",
                "Monaco",
                "United Kingdom", "Ireland", "Luxembourg", "Portugal", "Spain", "Belgium", "Israel", "Hungary",
                "Poland",
                "Slovakia", "Germany", "France", "The Netherlands"]

    # hc.povprecniVektor(skupina1)
    hc.run()
    hc.plot_tree()
