from matscholar import Rester

r = Rester('gobears!')
print(r.search({'material':['LiCoO2']}, limit=1))