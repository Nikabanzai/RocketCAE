# Heritage: CHEMA (2017) → RocketCAE (2026)

## Primary citation (original graduation project)

**Kul, M. A., Seymen, Y., Yıldız, M. E., Köroğlu, S. M., Balage, S., & Körpe, D. S.** (2017).  
*Preliminary Design, Basic Simulation and Optimization of Liquid Rocket Engines*  
[Technical report / graduation project]. University of Turkish Aeronautical Association.  
**DOI:** [10.13140/RG.2.2.31672.55043](https://doi.org/10.13140/RG.2.2.31672.55043)  
ResearchGate: ~9k reads (stats as of listing).

### Authors & affiliations (as of public ResearchGate profiles)

| Author | Role | Affiliation (public listing) |
|--------|------|------------------------------|
| Muhammed Ali Kul | Student author | Turkish Technic |
| Yağız Seymen | Student author | University of Turkish Aeronautical Association |
| Melih Emre Yıldız | Student author | (profile may be unclaimed on RG) |
| Süleyman Murat Köroğlu | Student author | Istanbul Technical University |
| S. (Sudantha) Balage | Advisor | Australian Defence Force Academy |
| Durmuş Sinan Körpe | Advisor | TAI - Turkish Aerospace Industries, Inc. |

Student IDs (from report): Kul 120 122 036 · Seymen 120 122 043 · Yıldız 120 122 056  
(Astronautical / Aeronautical Engineering, THK University.)

### What CHEMA was

- MATLAB GUIDE GUI (`ChemaV7`) calling legacy **CEA**
- LRE performance, chamber/nozzle (incl. **Rao nozzle** geometry figures), multi-objective optimization hooks
- Goal: explore many liquid engines and propose viable *preliminary* designs

### Open-source positioning of RocketCAE

RocketCAE is a **modern Python reimplementation of the CHEMA *concept***:

- New codebase (not a dump of MATLAB sources or media)
- Official NASA **`cea`** package (Apache-2.0) instead of CEA300.exe
- Streamlit GUI + CLI + RP-1311 validation + mission sizing helpers
- Credits CHEMA authors/advisors as **concept predecessors**; RocketCAE maintained as independent software

Please cite:

1. **CHEMA 2017** (DOI above) for the original project idea  
2. **NASA CEA / RP-1311** for the thermodynamics engine  
3. **RocketCAE** (this repo / CITATION.cff) for the modern tool  

## Local archive

`Chema/` on a developer machine (if present) is the original dump and is **gitignored**.

## Disclaimer

Same spirit as CHEMA: theoretical results may differ immensely from reality.
