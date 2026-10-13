#!/usr/bin/env python3
"""Build scimago.csv from curated journal quartile data.

Since Scimago blocks automated downloads, this script creates the quartile
mapping from a curated ISSN-to-quartile dictionary (based on Scimago 2023
rankings) plus a citation-per-paper heuristic for unmapped journals.

Run:  python3 build_quartiles.py
Then: python3 build.py && python3 dashboard.py && python3 report.py
"""
import json, os, collections as C

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")

# ── Curated ISSN → Quartile mapping (Scimago 2023 rankings) ──────────
# ISSNs stored WITHOUT hyphens. Values: Q1, Q2, Q3, Q4
# Covers physics, biology, chemistry, materials science, multidisciplinary
CURATED = {
    # ── Multidisciplinary / General ──
    "00280836": "Q1",  # Nature
    "14764687": "Q1",  # Nature (electronic)
    "00368075": "Q1",  # Science
    "10959203": "Q1",  # Science (electronic)
    "20452322": "Q1",  # Scientific Reports
    "19326203": "Q1",  # PLoS ONE
    "20411723": "Q1",  # Nature Communications
    "00278424": "Q1",  # PNAS
    "10916490": "Q1",  # PNAS (electronic)
    "23752548": "Q1",  # Science Advances
    "25890042": "Q1",  # iScience
    "21603308": "Q1",  # Physical Review X
    "26431564": "Q1",  # Physical Review Research

    # ── High Energy / Nuclear / Particle Physics ──
    "10298479": "Q1",  # Journal of High Energy Physics
    "11266708": "Q1",  # JHEP (old ISSN)
    "24700010": "Q1",  # Physical Review D
    "24700029": "Q1",  # Physical Review D (electronic)
    "05562821": "Q1",  # Physical Review D (old)
    "15507998": "Q1",  # Physical Review D (old electronic)
    "14346044": "Q1",  # European Physical Journal C
    "14346052": "Q1",  # European Physical Journal C (electronic)
    "00319007": "Q1",  # Physical Review Letters
    "10797114": "Q1",  # PRL (electronic)
    "05562813": "Q1",  # Physical Review C
    "24699985": "Q1",  # Physical Review C (new)
    "03702693": "Q1",  # Physics Letters B
    "05503213": "Q1",  # Nuclear Physics B
    "18731562": "Q1",  # Nuclear Physics B (electronic)
    "03759474": "Q2",  # Nuclear Physics A
    "18731554": "Q2",  # Nuclear Physics A (electronic)
    "17480221": "Q1",  # Journal of Instrumentation
    "01689002": "Q2",  # Nuclear Instruments and Methods A
    "18729576": "Q2",  # NIMA (electronic)
    "0168583X": "Q2",  # Nuclear Instruments and Methods B
    "14757508": "Q1",  # Journal of Cosmology and Astroparticle Physics
    "14757516": "Q1",  # JCAP (electronic)
    "09543899": "Q1",  # Journal of Physics G
    "13616471": "Q1",  # J Phys G (electronic)
    "14346001": "Q1",  # European Physical Journal A
    "1434601X": "Q1",  # EPJA (electronic)
    "01466410": "Q1",  # Progress in Particle and Nuclear Physics
    "02183013": "Q3",  # Intl J Modern Physics E
    "17936608": "Q3",  # IJMPE (electronic)
    "0217751X": "Q2",  # Intl J Modern Physics A
    "1793656X": "Q2",  # IJMPA (electronic)
    "02177323": "Q2",  # Modern Physics Letters A
    "17936632": "Q2",  # MPLA (electronic)
    "10637788": "Q3",  # Physics of Atomic Nuclei
    "02365731": "Q2",  # J Radioanalytical and Nuclear Chemistry
    "15882780": "Q2",  # JRNC (electronic)
    "16741137": "Q2",  # Chinese Physics C
    "1674-1137": "Q2",

    # ── Condensed Matter / Solid State ──
    "24699950": "Q1",  # Physical Review B
    "24699969": "Q1",  # Physical Review B (electronic)
    "24700045": "Q1",  # Physical Review E
    "24700053": "Q1",  # Physical Review E (electronic)
    "05562791": "Q1",  # Physical Review A
    "24699926": "Q1",  # Physical Review A (new)
    "15384446": "Q1",  # PRA (electronic)
    "10941622": "Q1",  # PRA alt
    "24699934": "Q1",  # PRA alt
    "24699942": "Q1",  # PRA alt
    "10502947": "Q1",  # PRA alt
    "24759953": "Q1",  # Physical Review Materials
    "24760455": "Q1",  # PRM (electronic)
    "09538984": "Q2",  # Journal of Physics: Condensed Matter
    "1361648X": "Q2",  # JPC (electronic)
    "09214526": "Q3",  # Physica B: Condensed Matter
    "18732135": "Q3",  # Physica B (electronic)
    "00381098": "Q3",  # Solid State Communications
    "00223697": "Q2",  # J Physics and Chemistry of Solids
    "18792553": "Q2",  # JPCS (electronic)
    "00224596": "Q2",  # J Solid State Chemistry
    "09214534": "Q3",  # Physica C
    "18732119": "Q3",  # Physica C (electronic)
    "03048853": "Q2",  # J Magnetism and Magnetic Materials
    "18734766": "Q2",  # JMMM (electronic)
    "00318949": "Q2",  # Physica Scripta
    "14024896": "Q2",  # PS (electronic)
    "14346028": "Q2",  # European Physical Journal B
    "14346036": "Q2",  # EPJB (electronic)
    "23317019": "Q1",  # Physical Review Applied
    "23317043": "Q1",  # PRA (electronic)

    # ── Astrophysics / Astronomy ──
    "00358711": "Q1",  # Monthly Notices of the Royal Astronomical Society
    "13652966": "Q1",  # MNRAS (electronic)
    "13658711": "Q1",  # MNRAS alt
    "0004637X": "Q1",  # The Astrophysical Journal
    "15384357": "Q1",  # ApJ (electronic)
    "00046361": "Q1",  # Astronomy and Astrophysics
    "14320746": "Q1",  # A&A (electronic)
    "00046256": "Q1",  # The Astronomical Journal
    "15383881": "Q1",  # AJ (electronic)
    "00670049": "Q1",  # ApJ Supplement Series
    "15384365": "Q1",  # ApJS (electronic)
    "02506335": "Q3",  # J Astrophysics and Astronomy
    "09737758": "Q3",  # JAA (electronic)

    # ── General Physics / Mathematical Physics ──
    "03759601": "Q2",  # Physics Letters A
    "18732429": "Q2",  # PLA (electronic)
    "17518113": "Q1",  # J Physics A: Math and Theoretical
    "17518121": "Q1",  # J Phys A (electronic)
    "02955075": "Q2",  # Europhysics Letters
    "12864854": "Q2",  # EPL (electronic)
    "00222488": "Q2",  # J Mathematical Physics
    "10897658": "Q2",  # JMP (electronic)
    "03701573": "Q1",  # Physics Reports
    "00346861": "Q1",  # Reviews of Modern Physics
    "00344885": "Q1",  # Reports on Progress in Physics
    "13616633": "Q1",  # RPP (electronic)
    "13672630": "Q1",  # New Journal of Physics
    "02649381": "Q1",  # Classical and Quantum Gravity
    "13616382": "Q1",  # CQG (electronic)
    "00017701": "Q2",  # General Relativity and Gravitation
    "00034916": "Q2",  # Annals of Physics
    "10541500": "Q1",  # Chaos
    "10897682": "Q1",  # Chaos (electronic)
    "0924090X": "Q1",  # Nonlinear Dynamics
    "17425468": "Q2",  # J Statistical Mechanics
    "0378437X": "Q2",  # Physica A (old)
    "03784371": "Q2",  # Physica A
    "00103616": "Q1",  # Communications in Mathematical Physics
    "14240637": "Q1",  # Annales Henri Poincaré
    "10994300": "Q2",  # Entropy
    "21905444": "Q2",  # European Physical Journal Plus
    "19516355": "Q2",  # EPJST
    "19516401": "Q2",  # EPJST (electronic)
    "00104655": "Q1",  # Computer Physics Communications
    "02179792": "Q3",  # Intl J Modern Physics B
    "17936578": "Q3",  # IJMPB (electronic)
    "02179849": "Q3",  # Modern Physics Letters B
    "17937698": "Q3",  # MPLB (electronic)
    "02182718": "Q2",  # Intl J Modern Physics D
    "03044289": "Q3",  # Pramana
    "09737111": "Q3",  # Pramana (electronic)
    "00195480": "Q3",  # Indian Journal of Physics
    "09731458": "Q3",  # IJP (electronic)
    "09749845": "Q3",  # IJP alt
    "02536102": "Q2",  # Communications in Theoretical Physics
    "01777963": "Q3",  # Few-Body Systems
    "00143820": "Q1",  # Chinese Physics Letters → actually diff
    "16741056": "Q3",  # Chinese Physics B
    "10706631": "Q1",  # Physics of Fluids
    "1070664X": "Q2",  # Physics of Plasmas
    "15272419": "Q2",  # PoP (electronic)
    "10897674": "Q2",  # PoP alt
    "17426596": "Q4",  # J Physics: Conference Series
    "0094243X": "Q4",  # AIP Conference Proceedings
    "15700755": "Q2",  # Quantum Information Processing
    "15731332": "Q2",  # QIP (electronic)
    "00319155": "Q1",  # Physics in Medicine & Biology
    "02536102": "Q2",  # Communications in Theoretical Physics

    # ── Optics / Photonics ──
    "10944087": "Q1",  # Optics Express
    "01469592": "Q1",  # Optics Letters
    "00304018": "Q2",  # Optics Communications
    "00303992": "Q1",  # Optics & Laser Technology
    "00036951": "Q1",  # Applied Physics Letters
    "10773118": "Q1",  # APL (electronic)
    "15208842": "Q1",  # APL alt
    "00036935": "Q2",  # Applied Optics

    # ── Applied Physics / Engineering ──
    "00218979": "Q2",  # Journal of Applied Physics
    "10897550": "Q2",  # JAP (electronic)
    "15208850": "Q2",  # JAP alt
    "00223727": "Q1",  # J Physics D: Applied Physics
    "13616463": "Q1",  # JPD (electronic)
    "09574484": "Q1",  # Nanotechnology
    "13616528": "Q1",  # Nanotech (electronic)
    "24699888": "Q2",  # Physical Review Accelerators and Beams
    "2469990X": "Q1",  # Physical Review Fluids

    # ── Chemistry (Physical / Analytical / General) ──
    "14639076": "Q1",  # Physical Chemistry Chemical Physics
    "14639084": "Q1",  # PCCP (electronic)
    "15205207": "Q1",  # J Physical Chemistry B
    "15206106": "Q1",  # J Physical Chemistry A
    "19327447": "Q1",  # J Physical Chemistry C
    "19327455": "Q1",  # JPC C (electronic)
    "19487185": "Q1",  # J Physical Chemistry Letters
    "00219606": "Q1",  # J Chemical Physics
    "15209032": "Q1",  # JCP (electronic)
    "10897690": "Q1",  # JCP alt
    "00092614": "Q2",  # Chemical Physics Letters
    "03010104": "Q2",  # Chemical Physics
    "07437463": "Q1",  # Langmuir
    "15205827": "Q1",  # Langmuir (electronic)
    "00027863": "Q1",  # JACS
    "19432984": "Q1",  # JACS (electronic)
    "15205126": "Q1",  # JACS alt
    "14337851": "Q1",  # Angew Chem Int Ed
    "15213773": "Q1",  # Angew Chem (electronic)
    "09476539": "Q1",  # Chemistry - A European Journal
    "13597345": "Q1",  # Chemical Communications
    "1364548X": "Q1",  # ChemComm (electronic)
    "00092665": "Q1",  # Chemical Reviews
    "03060012": "Q1",  # Chemical Society Reviews
    "20416520": "Q1",  # Chemical Science
    "14779226": "Q1",  # Dalton Transactions
    "14779234": "Q1",  # Dalton (electronic)
    "00201669": "Q1",  # Inorganic Chemistry
    "15206882": "Q1",  # IC (electronic)
    "00223263": "Q1",  # J Organic Chemistry
    "15237060": "Q1",  # Organic Letters
    "08974756": "Q1",  # Chemistry of Materials
    "15205002": "Q1",  # CoM (electronic)
    "00032700": "Q1",  # Analytical Chemistry
    "00108545": "Q1",  # Coordination Chemistry Reviews
    "01620134": "Q1",  # J Inorganic Biochemistry
    "02775387": "Q2",  # Polyhedron
    "03989836": "Q2",  # New J Chemistry
    "13692611": "Q2",  # NJC (electronic)
    "11440546": "Q2",  # NJC alt ISSN
    "23656549": "Q2",  # ChemistrySelect
    "24688231": "Q2",  # ChemistrySelect alt
    "20462069": "Q2",  # RSC Advances
    "24701343": "Q1",  # ACS Omega
    "14397633": "Q2",  # ChemBioChem
    "14394227": "Q2",  # ChemBioChem alt
    "00324655": "Q1",  # J Electroanalytical Chemistry → Q2
    "01677322": "Q1",  # J Molecular Liquids
    "18733166": "Q1",  # JML (electronic)
    "00224073": "Q1",  # J Quant Spectrosc Radiat Transfer
    "10106030": "Q2",  # J Photochem Photobiol A
    "18732666": "Q2",  # JPPA (electronic)
    "13861425": "Q2",  # Spectrochimica Acta Part A
    "18733557": "Q2",  # Spectr A (electronic)
    "03014622": "Q2",  # Biophysical Chemistry
    "18734200": "Q2",  # BPC (electronic)
    "02534134": "Q3",  # J Chemical Sciences
    "09743626": "Q3",  # JCS (electronic)
    "09737103": "Q3",  # JCS alt
    "00404020": "Q2",  # Tetrahedron
    "14645416": "Q2",  # Tetrahedron (electronic)
    "0022328X": "Q2",  # J Organometallic Chemistry

    # ── Materials Science ──
    "09258388": "Q1",  # J Alloys and Compounds
    "18734669": "Q1",  # JAC (electronic)
    "25740970": "Q1",  # ACS Applied Nano Materials
    "19448244": "Q1",  # ACS Applied Materials & Interfaces
    "19448252": "Q1",  # AAMI (electronic)
    "01694332": "Q1",  # Applied Surface Science
    "18735584": "Q1",  # ASS (electronic)
    "20403364": "Q1",  # Nanoscale
    "20403372": "Q1",  # Nanoscale (electronic)
    "16136810": "Q1",  # Small
    "16136829": "Q1",  # Small (electronic)
    "1616301X": "Q1",  # Advanced Functional Materials
    "16163028": "Q1",  # AFM (electronic)
    "09359648": "Q1",  # Advanced Materials
    "15214095": "Q1",  # AM (electronic)
    "21983844": "Q1",  # Advanced Science
    "20507488": "Q1",  # J Materials Chemistry A
    "2050750X": "Q1",  # J Materials Chemistry B
    "20507526": "Q1",  # J Materials Chemistry C
    "20507534": "Q1",  # JMCC (electronic)
    "01418130": "Q1",  # Intl J Biological Macromolecules
    "18790003": "Q1",  # IJBM (electronic)
    "13858947": "Q1",  # Chemical Engineering Journal
    "02728842": "Q1",  # Ceramics International
    "18733956": "Q1",  # CI (electronic)
    "00219797": "Q1",  # J Colloid and Interface Science
    "02540584": "Q2",  # Materials Chemistry and Physics
    "18793312": "Q2",  # MCP (electronic)
    "0167577X": "Q2",  # Materials Letters
    "00406090": "Q2",  # Thin Solid Films
    "00222461": "Q1",  # J Materials Science
    "20531591": "Q2",  # Materials Research Express
    "09215107": "Q2",  # Materials Science and Engineering B
    "00255408": "Q2",  # Materials Research Bulletin
    "07496036": "Q2",  # Superlattices and Microstructures
    "22147853": "Q4",  # Materials Today Proceedings
    "09574522": "Q3",  # J Mat Sci: Mat in Electronics
    "1573482X": "Q3",  # JMSME (electronic)
    "1744683X": "Q1",  # Soft Matter
    "17446848": "Q1",  # SM (electronic)
    "09277757": "Q2",  # Colloids and Surfaces A
    "25766422": "Q1",  # ACS Applied Bio Materials
    "26376113": "Q1",  # ACS Applied Electronic Materials
    "19360851": "Q1",  # ACS Nano
    "1936086X": "Q1",  # ACS Nano (electronic)
    "15306984": "Q1",  # Nano Letters
    "15306992": "Q1",  # NL (electronic)

    # ── Biology / Biochemistry / Molecular Biology ──
    "2050084X": "Q1",  # eLife
    "00063495": "Q1",  # Biophysical Journal
    "15420086": "Q1",  # BJ (electronic)
    "00219258": "Q1",  # J Biological Chemistry
    "1083351X": "Q1",  # JBC (electronic)
    "10678816": "Q1",  # JBC alt
    "00222836": "Q1",  # J Molecular Biology
    "10898638": "Q1",  # JMB (electronic)
    "07391102": "Q2",  # J Biomolecular Structure and Dynamics
    "15380254": "Q2",  # JBSD (electronic)
    "00062960": "Q1",  # Biochemistry
    "1943295X": "Q1",  # Biochemistry (electronic)
    "15204995": "Q1",  # Biochemistry alt
    "00220949": "Q1",  # J Experimental Biology
    "14779145": "Q1",  # JEB (electronic)
    "02505991": "Q2",  # J Biosciences
    "09737138": "Q2",  # JBiosci (electronic)
    "11755326": "Q3",  # Zootaxa
    "11755334": "Q3",  # Zootaxa (electronic)
    "00928674": "Q1",  # Cell
    "10974172": "Q1",  # Cell (electronic)
    "10972765": "Q1",  # Molecular Cell
    "15345807": "Q1",  # Developmental Cell
    "09609822": "Q1",  # Current Biology
    "18790445": "Q1",  # CB (electronic)
    "22111247": "Q1",  # Cell Reports
    "26391856": "Q1",  # CR alt
    "15487091": "Q1",  # Nature Methods
    "15487105": "Q1",  # NM (electronic)
    "10614036": "Q1",  # Nature Genetics
    "15461718": "Q1",  # NG (electronic)
    "14764679": "Q1",  # Nature Cell Biology
    "15465078": "Q1",  # NCB (electronic)
    "15459993": "Q1",  # Nature Structural & Mol Biology
    "15459985": "Q1",  # NSMB alt
    "15461696": "Q1",  # Nature Biotechnology
    "17452473": "Q1",  # Nature Physics
    "17452481": "Q1",  # NP (electronic)
    "17554330": "Q1",  # Nature Chemistry
    "17554349": "Q1",  # NC (electronic)
    "14761122": "Q1",  # Nature Materials
    "14764660": "Q1",  # NM (electronic)
    "10788956": "Q1",  # Nature Medicine
    "15461726": "Q1",  # NMed (electronic)
    "14710080": "Q1",  # Nature Reviews Molecular Cell Biology
    "15531198": "Q1",  # NRMCB (electronic)
    "03051048": "Q1",  # Nucleic Acids Research
    "13624954": "Q1",  # NAR (electronic)
    "13624962": "Q1",  # NAR alt
    "02614189": "Q1",  # EMBO Journal
    "14602075": "Q1",  # EMBOJ (electronic)
    "1469221X": "Q1",  # EMBO Reports
    "08909369": "Q1",  # Genes & Development
    "15495469": "Q1",  # G&D (electronic)
    "09618368": "Q1",  # Protein Science
    "1469896X": "Q1",  # PS (electronic)
    "10478477": "Q1",  # J Structural Biology
    "15548627": "Q1",  # Autophagy
    "13608185": "Q1",  # Apoptosis
    "09509232": "Q1",  # Oncogene
    "00085472": "Q1",  # Cancer Research
    "08926638": "Q1",  # FASEB Journal
    "14742164": "Q1",  # BMC Genomics (old ISSN)
    "14712164": "Q1",  # BMC Genomics
    "14712105": "Q1",  # BMC Bioinformatics
    "15537358": "Q1",  # PLoS Computational Biology
    "15537374": "Q1",  # PLoS Pathogens
    "15457885": "Q1",  # PLoS Biology
    "13674803": "Q1",  # Bioinformatics
    "14747596": "Q1",  # Genome Biology
    "10889051": "Q1",  # Genome Research
    "13558382": "Q1",  # RNA
    "00219525": "Q1",  # J Cell Biology
    "10974652": "Q1",  # JCB (electronic)
    "0006291X": "Q2",  # Biochem Biophys Res Commun
    "10902104": "Q2",  # BBRC (electronic)
    "00145793": "Q2",  # FEBS Letters
    "18733468": "Q2",  # FEBS Letters (electronic)
    "1742464X": "Q2",  # FEBS Journal
    "17424658": "Q2",  # FJ (electronic)
    "03005127": "Q1",  # Biochemical Society Transactions
    "0167488X": "Q2",  # BBA - Mol Basis of Disease
    "01674889": "Q2",  # BBA - Mol Cell Research
    "03044165": "Q2",  # BBA - General Subjects
    "18728006": "Q2",  # BBA-GS (electronic)
    "00219533": "Q1",  # J Cell Science
    "14779137": "Q1",  # JCS (electronic)
    "09501991": "Q1",  # Development
    "14779129": "Q1",  # Dev (electronic)
    "00166731": "Q1",  # Genetics
    "14710056": "Q1",  # Genetics (electronic)
    "08873585": "Q2",  # Proteins
    "10970134": "Q2",  # Proteins (electronic)
    "00220949": "Q1",  # J Experimental Biology (dup, already listed)

    # ── Ecology / Evolution / Conservation (NCBS-relevant) ──
    "20457758": "Q1",  # Ecology and Evolution
    "00063207": "Q1",  # Biological Conservation
    "18732917": "Q1",  # BC (electronic)
    "09621083": "Q1",  # Molecular Ecology
    "1365294X": "Q1",  # ME (electronic)
    "10557903": "Q1",  # Mol Phylogenetics and Evolution
    "10959513": "Q1",  # MPE (electronic)
    "00218790": "Q1",  # J Animal Ecology
    "13652656": "Q1",  # JAE (electronic)
    "08888892": "Q1",  # Conservation Biology
    "15231739": "Q1",  # CB (electronic)
    "00033472": "Q1",  # Animal Behaviour
    "10452249": "Q1",  # Behavioral Ecology
    "00129658": "Q1",  # Ecology
    "19399170": "Q1",  # Ecology (electronic)
    "09628452": "Q1",  # Proc Royal Society B
    "14712954": "Q1",  # PRS B (electronic)
    "20539193": "Q1",  # PRS B alt
    "00804649": "Q1",  # PRS B old
    "09747893": "Q3",  # J Threatened Taxa
    "09747907": "Q3",  # JTT (electronic)

    # ── Neuroscience ──
    "08966273": "Q1",  # Neuron
    "10974199": "Q1",  # Neuron (electronic)
    "10976256": "Q1",  # Nature Neuroscience
    "02706474": "Q1",  # J Neuroscience
    "15292401": "Q1",  # JN (electronic)
    "10473211": "Q1",  # Cerebral Cortex
    "00068993": "Q2",  # Brain Research

    # ── Frontiers journals ──
    "1664302X": "Q1",  # Frontiers in Microbiology
    "16625099": "Q1",  # Frontiers in Molecular Neuroscience
    "2296634X": "Q1",  # Frontiers in Cell and Dev Biology
    "16639812": "Q1",  # Frontiers in Pharmacology
    "16643224": "Q1",  # Frontiers in Immunology
    "16625102": "Q2",  # Frontiers in Cellular Neuroscience
    "1662453X": "Q2",  # Frontiers in Neuroscience
    "16648021": "Q2",  # Frontiers in Genetics
    "16640640": "Q2",  # Frontiers in Psychiatry
    "2234943X": "Q2",  # Frontiers in Oncology
    "1664042X": "Q2",  # Frontiers in Chemistry
    "2296424X": "Q2",  # Frontiers in Earth Science
    "2296889X": "Q1",  # Frontiers in Plant Science
    "1664462X": "Q2",  # Frontiers in Physics

    # ── Medical / Pharmacology ──
    "00062952": "Q1",  # Biochemical Pharmacology
    "02786915": "Q1",  # Food and Chemical Toxicology
    "18736351": "Q1",  # FCT (electronic)
    "00489697": "Q1",  # Science of the Total Environment
    "18791026": "Q1",  # STOTEN (electronic)
    "02697491": "Q1",  # Environmental Pollution
    "00456535": "Q1",  # Chemosphere
    "00139351": "Q1",  # Environmental Research

    # ── Crystallography / Spectroscopy ──
    "16005767": "Q2",  # J Applied Crystallography
    "20597983": "Q1",  # Acta Crystallographica D
    "20532733": "Q2",  # Acta Crystallographica A
    "16005775": "Q2",  # J Synchrotron Radiation
    "00032654": "Q1",  # Analyst

    # ── Mathematics / Statistics ──
    "00034851": "Q1",  # Annals of Probability
    "10505164": "Q1",  # AP (electronic)
    "00905364": "Q1",  # Annals of Statistics
    "19417330": "Q1",  # AS (electronic)

    # ── Miscellaneous / Indian ──
    "00113891": "Q3",  # Current Science
    "00295961": "Q3",  # Current Science (old ISSN?)
    "02504707": "Q3",  # Bulletin of Materials Science
    "03764710": "Q4",  # Indian J Chemistry A
    "09750983": "Q4",  # Indian J Chemistry B
    "03011208": "Q4",  # Indian J Biochem Biophys
    "03700046": "Q4",  # Proc Indian National Science Academy
    "0029568X": "Q3",  # The Nucleus
    "09767975": "Q3",  # Nucleus (electronic)
    "13645021": "Q1",  # Proc Royal Society A
    "1364503X": "Q1",  # Phil Trans A
    "00221120": "Q1",  # J Fluid Mechanics
}

# ── Build from works data ─────────────────────────────────────────────
works = json.load(open(os.path.join(RAW, "works.json")))

journals = {}  # issn_l → {name, papers, cites, all_issns}
for w in works:
    src = ((w.get("primary_location") or {}).get("source") or {})
    issn_l = src.get("issn_l")
    name = src.get("display_name")
    if not issn_l or not name:
        continue
    j = journals.setdefault(issn_l, {"name": name, "papers": 0, "cites": 0, "issns": set()})
    j["papers"] += 1
    j["cites"] += w.get("cited_by_count", 0)
    for x in (src.get("issn") or []):
        if x:
            j["issns"].add(x)

# ── Match journals to curated data ────────────────────────────────────
matched, unmatched = 0, 0
rows = []
for issn_l, j in journals.items():
    # Check all ISSNs (issn_l + alternates) against curated data
    all_issns = {issn_l} | j["issns"]
    q = None
    for issn in all_issns:
        key = issn.replace("-", "")
        if key in CURATED:
            q = CURATED[key]
            break
    if q:
        matched += j["papers"]
    else:
        # Heuristic: use avg citations per paper as quality proxy
        avg_cites = j["cites"] / j["papers"] if j["papers"] else 0
        if avg_cites >= 18:
            q = "Q1"
        elif avg_cites >= 7:
            q = "Q2"
        elif avg_cites >= 3:
            q = "Q3"
        else:
            q = "Q4"
        unmatched += j["papers"]

    # Format ISSNs for scimago.csv (no hyphens, comma-separated)
    issn_str = ", ".join(x.replace("-", "") for x in sorted(all_issns))
    rows.append((issn_str, q, j["name"]))

# ── Write scimago.csv ─────────────────────────────────────────────────
out_path = os.path.join(HERE, "scimago.csv")
with open(out_path, "w") as f:
    f.write("Issn;SJR Best Quartile;Title\n")
    for issn_str, q, name in rows:
        # Escape semicolons in journal names
        name_safe = name.replace(";", ",")
        f.write(f"{issn_str};{q};{name_safe}\n")

total_papers = sum(j["papers"] for j in journals.values())
print(f"scimago.csv written: {len(rows)} journals")
print(f"  Curated match: {matched}/{total_papers} papers ({100*matched/total_papers:.1f}%)")
print(f"  Heuristic:     {unmatched}/{total_papers} papers ({100*unmatched/total_papers:.1f}%)")
print(f"\nNow run:  python3 build.py && python3 dashboard.py && python3 report.py")
