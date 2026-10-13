"""Approximate 2023 Journal Impact Factors (JCR-style) keyed by ISSN without hyphens.

Used only to classify papers into IF > 5 and IF > 10. Journals not listed are
left as unlisted — they are not assumed to be below 5.
"""

# issn (no hyphen) -> IF
IF_BY_ISSN = {
    # multidisciplinary / flagship
    "00280836": 50.5, "14764687": 50.5,  # Nature
    "00368075": 47.7, "10959203": 47.7, "01934511": 47.7,  # Science
    "00928674": 45.5, "10974172": 45.5,  # Cell
    "20411723": 14.7,  # Nature Communications
    "23752548": 11.7,  # Science Advances
    "00278424": 9.4, "10916490": 9.4,  # PNAS
    "25890042": 5.1,  # iScience
    "20452322": 3.8,  # Scientific Reports
    "19326203": 2.9,  # PLoS ONE
    # nature / cell family
    "17452473": 19.6, "17452481": 19.6,  # Nature Physics
    "14764660": 64.8, "1474170X": 64.8,  # Nature Medicine
    "10614036": 31.7, "15461718": 31.7,  # Nature Genetics
    "15487091": 28.1, "15487105": 28.1,  # Nature Methods
    "17554330": 19.2, "17554349": 19.2,  # Nature Chemistry
    "14710072": 81.3, "14710080": 81.3,  # Nat Rev Mol Cell Biol
    "14741712": 78.5,  # Nat Rev Genet
    "14741756": 83.1,  # Nat Rev Immunol
    "17594774": 37.2,  # Nat Chem Biol
    "2397334X": 16.8,  # Nat Ecol Evol
    "2662138X": 42.1,  # Nat Rev Earth Env
    "22111247": 7.5,  # Cell Reports
    "20414889": 8.1,  # Cell Death and Disease
    # physics
    "00319007": 8.1, "10797114": 8.1, "10920145": 8.1,  # PRL
    "10298479": 5.4, "11266708": 5.4, "11272236": 5.4,  # JHEP
    "24700010": 5.0, "24700029": 5.0, "24700037": 5.0,  # PRD
    "24699950": 3.7, "24699969": 3.7,  # PRB
    "14346044": 4.4, "14346052": 4.4,  # EPJC
    "05562813": 3.1, "24699985": 3.1, "24699993": 3.1, "24700002": 3.1,  # PRC
    "03702693": 4.4, "18732445": 4.4,  # Physics Letters B
    "24700045": 2.4, "24700053": 2.4,  # PRE
    "17480221": 1.3,  # JINST
    "05562791": 2.9, "24699926": 2.9,  # PRA
    "00358711": 4.8, "13652966": 4.8,  # MNRAS
    "0004637X": 4.9, "15384357": 4.9,  # Astrophysical Journal
    "00670049": 8.8,  # ApJ Supplement
    "00046361": 5.8, "14320746": 5.8,  # A&A
    "14757508": 5.2, "14757516": 5.2,  # JCAP
    "21603308": 11.6,  # Physical Review X
    "26431564": 4.2,  # PR Research
    "23317019": 4.6,  # PR Applied
    "24759953": 3.4,  # PR Materials
    "05503213": 2.8, "18731562": 2.8,  # Nuclear Physics B
    "03759474": 1.4, "18731554": 1.4,  # Nuclear Physics A
    "09543899": 3.5, "13616471": 3.5,  # J Phys G
    "14346001": 3.0, "1434601X": 3.0,  # EPJA
    "21905444": 2.1,  # EPJ Plus
    "01689002": 1.4,  # NIMA
    "0168583X": 1.3,  # NIMB
    "1070664X": 2.0,  # Physics of Plasmas
    "00218979": 2.7,  # J Applied Physics
    "00036951": 3.5,  # Applied Physics Letters
    "00223727": 3.1,  # J Phys D
    "02955075": 1.8,  # EPL
    "09538984": 2.7, "1361648X": 2.7,  # JPCM
    "00318949": 2.6,  # Physica Scripta
    "09214526": 2.8,  # Physica B
    "03784371": 3.0,  # Physica A
    "03759601": 2.3,  # Physics Letters A
    "17425468": 2.2,  # JSTAT
    "02649381": 3.6,  # Classical and Quantum Gravity
    "00295515": 3.8,  # Nuclear Fusion
    "13672630": 2.8,  # New Journal of Physics
    "17518113": 2.1,  # J Phys A
    "00034916": 3.0,  # Annals of Physics
    "21983844": 14.3,  # Advanced Science
    "25424653": 4.6,  # SciPost Physics
    "2521327X": 6.4,  # Quantum
    "25119044": 4.4,  # Advanced Quantum Technologies
    # chemistry / materials
    "00027863": 14.4,  # JACS
    "15205126": 14.4,
    "14337851": 16.6, "15213773": 16.6,  # Angewandte Int Ed
    "09359648": 27.4, "15214095": 27.4,  # Advanced Materials
    "1616301X": 18.5, "16163028": 18.5,  # AFM
    "16136810": 13.3, "16136829": 13.3,  # Small
    "15306984": 10.8, "15306992": 10.8,  # Nano Letters
    "19360851": 15.8,  # ACS Nano
    "19448244": 8.5, "19448252": 8.5,  # ACS AMI
    "25740970": 5.3,  # ACS Applied Nano Materials
    "25766422": 4.7,  # ACS Applied Bio
    "25740962": 5.9,  # ACS Applied Energy
    "24701343": 3.7,  # ACS Omega
    "21680485": 7.1,  # ACS Sustainable Chem Eng
    "08974756": 8.6,  # Chemistry of Materials
    "20507488": 11.9,  # J Mater Chem A
    "20507526": 6.4,  # J Mater Chem C
    "20403364": 6.7,  # Nanoscale
    "01694332": 6.7,  # Applied Surface Science
    "13858947": 13.3,  # Chemical Engineering Journal
    "13597345": 4.9,  # Chem Comm
    "09258388": 6.2,  # Journal of Alloys and Compounds
    "01418130": 7.7,  # IJ Biological Macromolecules
    "01677322": 5.3,  # Journal of Molecular Liquids
    "15205207": 2.7,  # JPCB  (issn_l often 0022-3654)
    "00223654": 2.7,
    "19327447": 3.7,  # JPCC
    "19487185": 4.8,  # JPC Letters
    "14639076": 3.3,  # PCCP
    "20462069": 3.9,  # RSC Advances
    "09574484": 2.9,  # Nanotechnology
    "03048853": 2.7,  # JMMM
    "00219606": 3.1,  # J Chem Phys
    "07437463": 3.7,  # Langmuir
    "03989836": 3.3,  # New Journal of Chemistry
    "00062960": 2.9,  # Biochemistry
    "15204995": 2.9,
    "0006291X": 3.1,  # BBRC
    "02728842": 5.1,  # Ceramics International
    "23656549": 2.1,  # ChemistrySelect
    "07391102": 2.7,  # JBSD
    "20457758": 2.4,  # Ecology and Evolution
    "15700755": 2.5,  # Quantum Information Processing
    "1744683X": 2.9,  # Soft Matter
    "09618368": 3.2,  # Protein Science
    "14712164": 3.5,  # BMC Genomics
    "26376113": 4.3,  # ACS Applied Electronic Materials
    "14394227": 3.0,  # ChemBioChem
    "02365731": 1.5,  # JRNC
    "00219258": 4.0,  # JBC
    "00032700": 6.7,  # Analytical Chemistry
    "00201669": 4.3,  # Inorganic Chemistry
    "09476539": 3.9,  # Chem Eur J
    "14779226": 3.5,  # Dalton
    "09254005": 8.0,  # Sensors & Actuators B
    "00489697": 8.2,  # STOTEN
    # life / NCBS-heavy
    "2050084X": 6.4,  # eLife
    "00063495": 3.4,  # Biophysical Journal
    "00222836": 5.4,  # Journal of Molecular Biology
    "03051048": 14.9, "13624962": 14.9,  # Nucleic Acids Research
    "09609822": 8.1,  # Current Biology
    "02614189": 11.4,  # EMBO Journal
    "15449173": 7.8,  # PLoS Biology
    "15537390": 3.6,  # PLoS Genetics
    "00219525": 7.3,  # J Cell Biology
    "00219533": 3.3,  # J Cell Science
    "1742464X": 5.4,  # FEBS Journal
    "00063207": 5.9,  # Biological Conservation
    "1664302X": 5.2,  # Frontiers in Microbiology
    "16643224": 5.7,  # Frontiers in Immunology
    "23993642": 5.9,  # Communications Biology
    "00804649": 4.7,  # Proc R Soc B
    "00220949": 1.8,  # JEB
    "08926638": 4.8,  # FASEB
    "13596446": 7.4,  # Drug Discovery Today
    "09501991": 3.6,  # Development
    "14220067": 4.9,  # IJMS
    "00062952": 5.8,  # Biochemical Pharmacology
    "10591524": 3.0,  # MBoC
    "11755326": 1.0,  # Zootaxa
    "02505991": 1.5,  # Journal of Biosciences
}

# ---- added in the feedback round (Oct 2026): journals in our corpus that were missing above.
# Approximate JCR 2023 impact factors, keyed by the issn_l OpenAlex reports for our papers.
IF_BY_ISSN.update({
    # Nature / Cell / Science family and reviews (IF > 10)
    "07332229": 33.1,  # Nature Biotechnology
    "17483387": 38.1,  # Nature Nanotechnology
    "14657392": 17.3,  # Nature Cell Biology
    "15524450": 12.9,  # Nature Chemical Biology
    "14710056": 39.1,  # Nature Reviews Genetics
    "10976256": 21.2,  # Nature Neuroscience
    "2055026X": 15.8,  # Nature Plants
    "17502799": 13.1,  # Nature Protocols
    "2157846X": 26.8,  # Nature Biomedical Engineering
    "1758678X": 29.6,  # Nature Climate Change
    "23973366": 12.9,  # Nature Astronomy
    "23989629": 25.7,  # Nature Sustainability
    "08966273": 14.7,  # Neuron
    "15345807": 10.7,  # Developmental Cell
    "09628924": 19.0,  # Trends in Cell Biology
    "01695347": 16.7,  # Trends in Ecology & Evolution
    "19466234": 15.8,  # Science Translational Medicine
    "00092665": 51.4,  # Chemical Reviews
    "03060012": 40.4,  # Chemical Society Reviews
    "00108545": 20.3,  # Coordination Chemistry Reviews
    "03701573": 23.9,  # Physics Reports
    "00665154": 12.1,  # Annual Review of Biochemistry
    "10810706": 11.4,  # Annual Review of Cell and Developmental Biology
    "1543592X": 11.2,  # Annual Review of Ecology, Evolution and Systematics
    "15317331": 10.6,  # Annual Review of Materials Research
    "00664286": 9.1,   # Annual Review of Phytopathology
    "00063231": 11.0,  # Biological Reviews
    "01686445": 10.1,  # FEMS Microbiology Reviews
    "00335835": 7.2,   # Quarterly Reviews of Biophysics
    "01677659": 7.7,   # Cancer and Metastasis Reviews
    "15548627": 14.6,  # Autophagy
    "00085472": 12.5,  # Cancer Research
    "10780432": 10.4,  # Clinical Cancer Research
    "03043835": 9.1,   # Cancer Letters
    "23266066": 8.1,   # Cancer Immunology Research
    "13509047": 13.7,  # Cell Death and Differentiation
    "03923078": 11.4,  # J Experimental & Clinical Cancer Research
    "00431354": 11.4,  # Water Research
    "03043894": 12.2,  # Journal of Hazardous Materials
    "22112855": 16.8,  # Nano Energy
    "00016686": 15.9,  # Advances in Colloid and Interface Science
    "16146832": 24.4,  # Advanced Energy Materials
    "21502551": 31.6,  # Nano-Micro Letters
    "23808195": 19.3,  # ACS Energy Letters
    "21555435": 11.3,  # ACS Catalysis
    "23747943": 12.7,  # ACS Central Science
    "19311401": 11.9,  # Applied Physics Reviews
    "00086223": 10.5,  # Carbon
    "09565663": 10.7,  # Biosensors and Bioelectronics
    "22132317": 10.7,  # Redox Biology
    "10404651": 10.0,  # The Plant Cell
    "07374038": 11.0,  # Molecular Biology and Evolution
    "14639262": 9.3,   # Green Chemistry
    "09601481": 9.0,   # Renewable Energy
    "26911399": 9.3,   # PRX Quantum
    "20901224": 11.4,  # Journal of Advanced Research
    "24686069": 9.0,   # Materials Today Energy
    "25888420": 8.2,   # Materials Today Nano
    "21922640": 10.0,  # Advanced Healthcare Materials
    # IF 5-10
    "20416520": 7.6,   # Chemical Science
    "13596454": 8.3,   # Acta Materialia
    "03787753": 8.1,   # Journal of Power Sources
    "03088146": 8.5,   # Food Chemistry
    "00456535": 8.1,   # Chemosphere
    "0028646X": 8.3,   # New Phytologist
    "00139351": 7.7,   # Environmental Research
    "10436618": 9.1,   # Pharmacological Research
    "07533322": 6.9,   # Biomedicine & Pharmacotherapy
    "09509232": 6.9,   # Oncogene
    "00222623": 6.8,   # Journal of Medicinal Chemistry
    "19379145": 6.7,   # Science Signaling
    "0893133X": 6.6,   # Neuropsychopharmacology
    "1469221X": 6.5,   # EMBO Reports
    "00320889": 6.5,   # Plant Physiology
    "2041210X": 6.3,   # Methods in Ecology and Evolution
    "1466822X": 6.3,   # Global Ecology and Biogeography
    "09270248": 6.3,   # Solar Energy Materials and Solar Cells
    "01476513": 6.2,   # Ecotoxicology and Environmental Safety
    "10849521": 6.2,   # Seminars in Cell and Developmental Biology
    "09445013": 6.1,   # Microbiological Research
    "20587716": 6.1,   # Cell Death Discovery
    "02235234": 6.0,   # European Journal of Medicinal Chemistry
    "09550674": 6.0,   # Current Opinion in Cell Biology
    "22136711": 5.9,   # Stem Cell Reports
    "00220957": 5.6,   # Journal of Experimental Botany
    "00207136": 5.7,   # International Journal of Cancer
    "15537366": 5.5,   # PLoS Pathogens
    "15257797": 5.5,   # Biomacromolecules
    "00134686": 5.5,   # Electrochimica Acta
    "09284931": 5.5,   # Materials Science & Engineering C
    "09628436": 5.4,   # Phil Trans R Soc B
    "09277765": 5.4,   # Colloids and Surfaces B
    "00220477": 5.3,   # Journal of Ecology
    "00219797": 9.4,   # Journal of Colloid and Interface Science
    "18645631": 7.5,   # ChemSusChem
    "08915849": 7.1,   # Free Radical Biology and Medicine
    "20417798": 7.9,   # ApJ Letters (issn_l)
    "20418205": 7.9,   # ApJ Letters
    "24054712": 9.0,   # Cell Systems
    "22126864": 5.0,   # Physics of the Dark Universe
    "00218901": 5.0,   # Journal of Applied Ecology
    "09441344": 5.8,   # Environmental Science and Pollution Research
    "26335409": 5.2,   # Materials Advances
    "00216561": 5.7,   # Journal of Agricultural and Food Chemistry
    "20531400": 3.5,   # Env Sci Water Res Tech
    "20518153": 5.8,   # Environmental Science: Nano
    "17489326": 5.8,   # Environmental Research Letters
    "08866236": 5.4,   # Global Biogeochemical Cycles
    "23973722": 8.5,   # npj Climate and Atmospheric Science
    "20524110": 4.6,   # Organic Chemistry Frontiers
    "23304022": 6.5,   # ACS Photonics
    "26394979": 9.6,   # ACS Materials Letters
    "23793694": 8.2,   # ACS Sensors
    "2365709X": 6.4,   # Advanced Materials Technologies
    "14752859": 4.3,   # Microbial Cell Factories
    "10665099": 4.0,   # Stem Cells
    "1420682X": 6.2,   # Cellular and Molecular Life Sciences
    "20726694": 4.5,   # Cancers
    "03605442": 9.0,   # Energy
    "0038092X": 6.0,   # Solar Energy
    "03401573": 4.6,   # Cancer Immunology Immunotherapy
    "09598049": 7.6,   # European Journal of Cancer
    "17576512": 7.1,   # Stem Cell Research & Therapy
    "01407791": 6.0,   # Plant Cell & Environment
    "00483575": 4.2,   # Pesticide Biochem Physiol
    # IF < 5 but frequent in our corpus (so they are no longer "unlisted")
    "02786915": 3.9, "02646021": 4.4, "20545703": 2.9, "2296889X": 3.9, "08887543": 3.4, "21583226": 1.4,
    "1553734X": 3.8, "00052736": 2.8, "15287483": 3.2, "2296634X": 4.6, "22147500": 3.8, "13522310": 4.2,
    "10541500": 2.7, "00320935": 3.6, "17596653": 3.2, "16639812": 4.4, "2296701X": 2.4, "16808584": 3.0,
    "01674412": 3.9, "00243205": 5.2, "01689452": 4.2, "10111344": 3.9, "23795042": 3.7, "00189464": 2.1,
    "19487193": 4.1, "18672450": 4.9, "00222461": 3.5, "18673880": 3.8, "02706474": 4.4, "13674803": 4.4,
    "14712105": 2.9, "17527155": 3.4, "1530437X": 4.3, "00046256": 5.1, "00032654": 3.6, "03005127": 3.9,
    "0893228X": 3.7, "01448463": 4.0, "22962646": 3.8, "00166731": 3.3, "14203049": 4.2, "13645021": 2.9,
    "19492553": 0.0, "03050270": 3.4, "25160230": 4.6, "13877003": 4.4, "09594388": 4.8, "00033472": 2.3,
    "15476286": 3.6, "1364503X": 4.3, "17422051": 3.0, "00030147": 2.4, "13132970": 1.1, "14625814": 2.6,
    "2050750X": 6.1, "11779322": 2.3, "01698095": 4.5, "07217595": 3.9, "19352727": 3.4, "01664328": 2.6,
    "01469592": 3.1, "13989219": 3.6, "16625099": 3.5, "03008177": 3.5, "00223751": 4.7, "12932558": 3.4,
    "00143820": 3.1, "09276505": 4.2, "24520144": 1.3, "10557903": 3.6, "00219541": 4.5, "03438651": 2.3,
    "00144827": 3.3, "24055808": 2.3, "09603115": 3.1, "09516433": 5.0, "00778923": 4.1, "00189383": 2.9,
    "23522895": 4.3, "00223263": 3.3, "13698001": 4.2, "14712407": 3.4, "13608185": 6.1, "03788741": 4.8,
    "00201693": 2.7, "0924090X": 5.2, "10465928": 1.4, "20402392": 6.3, "00796107": 3.2, "23739878": 5.4,
    "08885885": 3.8, "03405761": 4.8, "15499634": 4.2, "00447447": 5.8, "07217714": 4.5, "00320781": 3.9,
    "09621083": 4.5, "00128658": 4.4, "16121011": 1.4, "00063568": 7.6, "20462441": 4.5,
    "0026265X": 4.9, "22352988": 4.6, "12864579": 2.6, "17456150": 4.4, "19491034": 3.4, "00093084": 3.4,
    "09552863": 4.8, "16642392": 3.9, "1010061X": 2.1, "00199567": 2.9, "00468991": 2.1, "01620134": 3.8,
    "00221503": 2.6, "15237052": 4.9, "19475705": 4.5, "03603199": 8.1, "18777503": 3.1, "09646906": 3.1,
    "16625153": 2.6, "14396092": 1.6, "09645691": 4.8, "00195464": 0.5, "08991987": 3.0, "10527613": 2.5,
    "01718630": 2.3, "0300483X": 4.8,
    "22147853": 0.0, "02534134": 1.7, "20531591": 1.8, "00223697": 4.3, "02183013": 1.0, "03044289": 1.9,
    "0217751X": 1.4, "00195480": 1.6, "08873585": 3.2, "03044165": 2.8, "09747893": 0.9, "02506335": 1.1,
    "02177323": 1.4, "0029568X": 0.0, "02540584": 4.3, "10106030": 4.1, "03014622": 3.3, "09574522": 2.8,
    "00404020": 2.1, "13861425": 4.3, "19516355": 2.6, "23318325": 1.0, "00086215": 2.4, "07403224": 1.8,
    "09478396": 2.5, "14394235": 2.3, "00017701": 2.1, "00255408": 5.3, "1940087X": 1.2, "0042207X": 3.8,
    "13869477": 2.9, "03615235": 2.2, "13500872": 2.6, "00063606": 1.8, "02198878": 2.1, "00448249": 0.0,
    "00113891": 0.8, "02731177": 2.8, "00194964": 1.7, "2190572X": 2.6, "14770520": 2.9, "15709639": 2.8,
    "00222313": 3.3, "14346028": 1.6, "00039276": 2.3, "2296424X": 1.9, "0004640X": 1.8, "09732063": 0.0,
    "20532733": 1.9, "23732822": 2.7, "15499596": 5.6, "25751077": 3.3, "09669795": 4.3, "09485023": 2.1,
    "00092614": 2.8, "17837620": 0.0, "00221767": 3.6,
})
_ = [IF_BY_ISSN.pop(k) for k, v in list(IF_BY_ISSN.items()) if v == 0.0]   # 0.0 = journal has no JCR impact factor

_IF = {k.replace("-", "").replace(" ", "").upper(): v for k, v in IF_BY_ISSN.items()}


def norm_issn(s):
    return (s or "").replace("-", "").replace(" ", "").upper()


def impact_factor(issn):
    x = norm_issn(issn)
    return _IF.get(x) if x else None


def if_band(ifv):
    if ifv is None:
        return "unlisted"
    if ifv > 10:
        return "gt10"
    if ifv > 5:
        return "gt5"
    return "lt5"
