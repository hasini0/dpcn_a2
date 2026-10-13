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
    "00032500": 6.7,  # Analytical Chemistry
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
