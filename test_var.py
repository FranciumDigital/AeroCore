from SimConnect import *

def test_simvar_disponibilite(nom_variable):
    try:
        sm = SimConnect()
        aq = AircraftRequests(sm, _time=2000)

        valeur = aq.get(nom_variable)
        print(f"✅ La variable '{nom_variable}' est disponible. Valeur lue : {valeur}")
    except Exception as e:
        print(f"❌ La variable '{nom_variable}' est indisponible ou invalide.")
        print(f"Erreur : {e}")

if __name__ == "__main__":
    # ➤ Teste ici n’importe quelle SimVar que tu veux vérifier
    test_simvar_disponibilite("IS_ACTIVE_PAUSE")
