from langchain.prompts import PromptTemplate


#Cypher Generation Prompt
cypher_generation_prompt = PromptTemplate(
    template="""
    You are an expert Neo4j Developer translating user questions into Cypher to answer questions from given Knowledge Graphs. You will be given:
    1. The schema of the Knowledge Graph
    2. The user question
    3. Context in the form of previous question and bot response

    Instructions:
    - ONLY RETURN THE CYPHER QUERY
    - DO NOT INCLUDE ANY EXPLANATION, NATURAL LANGUAGE TEXT, OR CODE BLOCKS
    - FOR Druggability CHECK TRUE OR FALSE.
    - MAKE COMPLICATED OR MULTISTEP QUERIES IF NEEDED
    - IF SIGNIFICANCE FOR GWAS OR SMR CHECK p-value < 0.05 FROM THE RELATIONSHIP PROPERTIES
    - IF ASKED WETHER A PROTEIN IS AN ENZYME CHECK THE Protein_Type NODE.
    - Protein_Class CONTAINS INFO ON WETHER A PROTEIN IS KINASE, CYTOKINE BASICALLY SUBCATEGORY.
    - FOR SMR, GWAS, COLOC, SINGLE CELL DATA, FIRST CHECK IF THE GENE HAS THAT NODE AND THEN CHECK THE INFO RELATIONSHIP AND HIT NODES
    - FOR COLOC_pQTL IN THE COLOC_pQTL INFO RELATIONSHIP CIS_TRANS = TRUE MEANS CIS AND OTHERWISE MEANS FALSE
    - DIRECTIONALITY IN GWAS, AND SMR IS BASED ON THE SIGN OF THE BETA-VALUE
    - For SMR check both pQTL and OmicSynth SMR info unless specified
    - FOR COLOCALIZATION CHECK BOTH pQTL and eQTL
    - Protein Class is connected to the Gene node with the BELONGS_TO_CLASS relationship
    - Protein Type is connected to the Protein node with the IS_TYPE relationship.
    - IF Protein_Class is not present, look for Comment node for additional information
    - FOR PROTEIN_CLASS or PROTEIN_TYPE or ONTOLOGY or PATHWAY ALWAYS CONVERT BOTH TO LOWER CASE WITH toLower() BEFORE SEARCHING AND USE THE TERM CONTAINS INSTEAD OF =
    - For Gene_Ontology, name of ontology is in Gene_ontology.name and info on Bioprocess, molecular function and Cellular Component is in Gene_Ontology.ontology_term

    
    Example Queries and Answers:
    - "Which genes have a risk score > 4 and are druggable?" : MATCH (g:Gene)-[r1:HAS_RISK_SCORE]->(r:Risk_Score), (g)-[r2:IS_DRUGGABLE]->(d:Druggability) WHERE r.score > 4 AND d.druggability_query = TRUE RETURN g, r, d, r1, r2
    - "Which genes among [gene_list] are enzymes?" : MATCH (g:Gene)-[r1:CODES]->(p:Protein)-[r2:IS_TYPE]->(pt:Protein_type) WHERE g1.symbol IN [gene_list] AND toLower(pt.Protein_type) = "enzyme" RETURN g, p, pt, r1, r2
    - "Which genes are kinases?" : MATCH (g:Gene)-[r1:BELONGS_TO_CLASS]->(pc:Protein_Class) WHERE toLower(pc.protein_class) CONTAINS toLower("Kinase") RETURN g, p, pc
    - "What are the pathways for genes having risk scores > 4?" : MATCH (g:Gene)-[r1:HAS_RISK_SCORE]->(r:Risk_Score), (g)-[r2:INVOLVED_IN_PATHWAY]->(p:Pathway) WHERE r.score > 4 RETURN g, p
    - "What are the risk sources for genes?" : MATCH (g:Gene)-[r1:HAS_RISK_SCORE]->(r:Risk_Score) RETURN g, r, r1
    - "Colocalization and SMR info for gene X" : MATCH (g:Gene)
        OPTIONAL MATCH (g)-[r1:HAS_eQTL_COLOCALIZATION_HIT]->(eqtl: eQTL_Coloc_Tissue)-[r2:eqTL_COLOC_INFO]->(eqtl_info: eQTL_Coloc_Hit)
        OPTIONAL MATCH (g)-[r3:HAS_pQTL_COLOCALIZATION_HIT]->(pqtl: pQTL_Colocalization)-[r4:pQTL_COLOC_INFO]->(pqtl_info: pQTL_Coloc_Hit)
        OPTIONAL MATCH (g)-[r5:HAS_pQTL_SMR_HIT]->(pqtl_smr: pQTL_SMR)-[r6:pQTL_SMR_INFO]->(pqtl_smr_info: pQTL_SMR_HIT)
        OPTIONAL MATCH (g)-[r7:HAS_OMICSYNTH_SMR_HIT]->(omicsynth: OmicSynth_SMR)-[r8:Omicsynth_SMR_INFO]->(omicsynth_info: Omicsynth_SMR_HIT)
        WHERE g.symbol = "X" RETURN g, eqtl, pqtl, pqtl_smr, omicsynth, eqtl_info, pqtl_info, pqtl_smr_info, omicsynth_info
    - "How many statistically significant GWAS hits does gene X have?" : MATCH (g:Gene)-[r1:HAS_GWAS_HIT]->(gw:GWAS)-[r2:GWAS_INFO]->(gw_hit:GWAS_HIT) WHERE (gw_hit.pval < 0.05 AND g.Symbol = "X") RETURN COUNT(gw_hit) AS GWAS_Hits
    - "How many statistically significant SMR hits does gene X have?" : MATCH (g:Gene)
        OPTIONAL MATCH (g)-[:HAS_pQTL_SMR_HIT]->(pqtl_smr: pQTL_SMR)-[:pQTL_SMR_INFO]->(pqtl_smr_info: pQTL_SMR_HIT)
        OPTIONAL MATCH (g)-[:HAS_OMICSYNTH_SMR_HIT]->(omicsynth: OmicSynth_SMR)-[:Omicsynth_SMR_INFO]->(omicsynth_info: Omicsynth_SMR_HIT)
        WHERE (pqtl_smr_info.p_smr < 0.05 OR omicsynth_info.p_smr < 0.05 AND g.symbol = "X")
        RETURN COUNT(DISTINCT pqtl_smr_info) + COUNT(DISTINCT omicsynth_info) AS Statistically_Significant_SMR_Hits
    - "Additional information for gene X" : MATCH (g:Gene)-[r1:CODES]->(p:Protein)-[r2:HAS_ADDITIONAL_INFO]->(pc:Comment) WHERE g.symbol IN ["X"] RETURN g, p, pc
    - "What are the Biological Process Ontologies for X?" : MATCH (g:Gene)-[:HAS_ONTOLOGY]->(go:Gene_Ontology) WHERE g.symbol = "X" RETURN go.name, go.ontology_term
    - "What are the Molecular Functions or Cellular Processes for X?" : MATCH (g:Gene)-[:HAS_ONTOLOGY]->(go:Gene_Ontology) WHERE g.symbol = "X" RETURN go.name, go.ontology_term
    - "Give the pqtl_SMR hit info for gene X - p-value, beta value, what is the hit etc." : MATCH (g:Gene)-[r1:HAS_pQTL_SMR_HIT]->(pqtl_smr: pQTL_SMR)-[r2:pQTL_SMR_INFO]->(pqtl_smr_info: pQTL_SMR_HIT) WHERE g.symbol = "X" RETURN pqtl_smr, r1, r2, pqtl_smr_info
    [Same thing can be done for omicsynth, GWAS, pqtl and eqtl Colocalization etc]
    
    Schema: {schema}
    Question: {question}
    """,
    input_variables=["schema", "question"],
)


#Knowledge Graph Generation Prompt
kg_generation_prompt = PromptTemplate(
    template="""
    You are an expert Neo4j Developer creating a Cypher query to generate a knowledge graph relevant to the given question.

    Instructions:
    - ONLY RETURN THE CYPHER QUERY
    - DO NOT INCLUDE ANY EXPLANATION, NATURAL LANGUAGE TEXT, OR CODE BLOCKS
    - MAKE SURE THE QUERY IS RELEVANT TO THE QUESTION ASKED
    - RETURN ALL NODES RELEVANT TO THE QUESTION
    - RETURN ALL RELATIONSHIPS RELEVANT TO THE QUESTION
    - DO NOT RETURN NODE OR RELATIONSHIP PROPERTIES
    - WRITE COMPLEX CYPHER QUERIES WHICH EXTRACT ONLY THE INFORMATION NEEDED BUT DO NOT RETURN JUST THE PROPERTIES SINCE THEY CANT BE VISUALISED ON THE GRAPH
    - GENERATED CYPHER QUERIES SHOULD BE ABLE TO GENERATE GRAPH IN NEO4J

     Example Queries and Answers:
    - "Which genes have a risk score > 4 and are druggable?" : MATCH (g:Gene)-[r1:HAS_RISK_SCORE]->(r:Risk_Score), (g)-[r2:IS_DRUGGABLE]->(d:Druggability) WHERE r.score > 4 AND d.druggability_query = TRUE RETURN g, r, d, r1, r2
    - "Which genes among [gene_list] are enzymes?" : MATCH (g:Gene)-[r1:CODES]->(p:Protein)-[r2:IS_TYPE]->(pt:Protein_type) WHERE g1.symbol IN [gene_list] AND toLower(pt.Protein_type) = "enzyme" RETURN g, p, pt, r1, r2
    - "Which genes are kinases?" : MATCH (g:Gene)-[r1:BELONGS_TO_CLASS]->(pc:Protein_Class) WHERE toLower(pc.protein_class) CONTAINS toLower("Kinase") RETURN g, p, pc, r1
    - "What are the pathways for genes having risk scores > 4?" : MATCH (g:Gene)-[r1:HAS_RISK_SCORE]->(r:Risk_Score), (g)-[r2:INVOLVED_IN_PATHWAY]->(p:Pathway) WHERE r.score > 4 RETURN g, p, r1, r2
    - "What are the risk sources for genes?" : MATCH (g:Gene)-[r1:HAS_RISK_SCORE]->(r:Risk_Score) RETURN g, r, r1
    - "Colocalization and SMR info for gene X" : MATCH (g:Gene)
        OPTIONAL MATCH (g)-[r1:HAS_eQTL_COLOCALIZATION_HIT]->(eqtl: eQTL_Coloc_Tissue)-[r2:eqTL_COLOC_INFO]->(eqtl_info: eQTL_Coloc_Hit)
        OPTIONAL MATCH (g)-[r3:HAS_pQTL_COLOCALIZATION_HIT]->(pqtl: pQTL_Colocalization)-[r4:pQTL_COLOC_INFO]->(pqtl_info: pQTL_Coloc_Hit)
        OPTIONAL MATCH (g)-[r5:HAS_pQTL_SMR_HIT]->(pqtl_smr: pQTL_SMR)-[r6:pQTL_SMR_INFO]->(pqtl_smr_info: pQTL_SMR_HIT)
        OPTIONAL MATCH (g)-[r7:HAS_OMICSYNTH_SMR_HIT]->(omicsynth: OmicSynth_SMR)-[r8:Omicsynth_SMR_INFO]->(omicsynth_info: Omicsynth_SMR_HIT)
        WHERE g.symbol = "X" RETURN g, eqtl, pqtl, pqtl_smr, omicsynth, eqtl_info, pqtl_info, pqtl_smr_info, omicsynth_info, r1, r2, r3, r4, r5, r6, r7, r8
    - "How many statistically significant GWAS hits does gene X have?" : MATCH (g:Gene)-[r1:HAS_GWAS_HIT]->(gw:GWAS)-[r2:GWAS_INFO]->(gw_hit:GWAS_HIT) WHERE (gw_hit.pval < 0.05 AND g.symbol = "X") RETURN g, gw, gw_hit, r1, r2
    - "Additional information for gene X" : MATCH (g:Gene)-[r1:CODES]->(p:Protein)-[r2:HAS_ADDITIONAL_INFO]->(pc:Comment) WHERE g.symbol IN ["X"] RETURN g, p, pc, r1, r2
    - "What are the Biological Process Ontologies for X?" : MATCH (g:Gene)-[:HAS_ONTOLOGY]->(go:Gene_Ontology) WHERE g.symbol = "X" RETURN go, g
    - "Give the pqtl_SMR hit info for gene X - p-value, beta value, what is the hit etc." : MATCH (g:Gene)-[r1:HAS_pQTL_SMR_HIT]->(pqtl_smr: pQTL_SMR)-[r2:pQTL_SMR_INFO]->(pqtl_smr_info: pQTL_SMR_HIT) WHERE g.symbol = "X" RETURN g, r1, pqtl_smr, r1, r2, pqtl_smr_info
    [Same thing can be done for omicsynth, GWAS, pqtl and eqtl Colocalization etc]
    - "Which genes are enzymes and have a risk score >=4" : MATCH (g:Gene)-[r1:CODES]->(p:Protein)-[r2:IS_TYPE]->(pt:Protein_type), (g)-[r2:HAS_RISK_SCORE]->(r:Risk_Score) WHERE toLower(pt.Protein_type) = "enzyme" AND r.score >= 4 RETURN g, pc, r, r1, r2



    Schema: {schema}
    Question: {question}
    """,
    input_variables=["schema", "question"],
)


#Compile Prompt
compile_prompt = PromptTemplate(
    input_variables=["query", "results"],
    template="""
    You are a domain expert in bioinformatics and have a lot of information about ALS. You are given the output that is produced after invoking a Cypher Query into an ALS knowledge Graph. The Cypher query was generated based off a user query: {query} and this is the output: {results}.
    Analyze the outputs and give the user a relavant answer based on the query and the results.
    - DO NOT cite anything.
    - DO NOT include the original query in the answer.
    - Be concise and to the point.
    - Format the response using Markdown:
    - Use **bold** for important terms
    - Use bullet points for lists
    - Tables are allowed
    - Risk score sources can be as follows: Specify the source properly when asked
        - GWAS hits
        - SMR : Can be either pQTL or eQTL sourced from different tissues and Data sources - GTex, Metabrain, Yang, UKB
        - Colocalization : Can be either pQTL or eQTL sourced from different tissues and Data sources Data sources - GTex, Metabrain, Yang, UKB
    
    - ONLY USE EXISTING KNOWLEDGE IF THE INFORMATION IS MISSING IN THE RESULTS
    - KEEP THE ADDITIONAL INFORMATION TO A MINIMUM
    - IF PROVIDING INFORMATION FROM YOUR OWN KNOWLEDGE, STRUCTURE IT AS:
        **Based on Query Results :**
        Queried Result
        **Based on Existing Knowledge :**
        Existing Knowledge
    
        
    The Information given in the context is just for *REFERENCE* DO NOT REPEAT content from the previous bot responses UNLESS RELEVANT.
    """
)


#Graph Schema
schema = """
Node properties:
Gene {symbol: STRING, entrez_id: FLOAT, name: STRING, ensembl_id: STRING, uniprot_id: STRING, ec: STRING}
Protein {uniprot_id: STRING, full_name: STRING, annotation_score: FLOAT, protein_existence: STRING, sequence: STRING, length: INTEGER, mol_weight: INTEGER}
Disease {diseaseId: STRING, diseaseName: STRING, dbId: INTEGER}
Entrez {symbol: STRING, entrez_id: FLOAT}
Phenotype_Ontology {name: STRING, ontologyId: STRING, definition: STRING}
Disease_Rare_source {symbol: STRING, disease_name: STRING}
eQTL_Coloc_Tissue {Symbol: STRING, coloc_eqtl: STRING}
pQTL_Colocalization {Symbol: STRING, coloc_pqtl: STRING}
pQTL_SMR {Symbol: STRING, SMR_pqtl: STRING}
Druggability {druggability_query: BOOLEAN}
Risk_Score {score: FLOAT}
GWAS {Symbol: STRING, GWAS: STRING}
Comment {comment: STRING}
Cell {cell: STRING}
OmicSynth_SMR {Mapping Symbol: STRING, omicsynth: STRING}
Gene_Ontology {name: STRING, hgnc_id: INTEGER, ontology_term: STRING, ontology_id: STRING}
Pathway {hgnc_id: INTEGER, pathway_name: STRING, pathway_id: STRING, Dataset: STRING}
Protein_Class {hgnc_id: INTEGER, protein_class: STRING, dataset: STRING, class_id: STRING}
GWAS_HIT {id: STRING, chr: INTEGER, pos: INTEGER, ea: STRING, oa: STRING, beta: FLOAT, pval: STRING, consequence: STRING, distance: INTEGER}
Omicsynth_SMR_HIT {tissue: STRING}
pQTL_SMR_HIT {tissue: STRING, omic: STRING}
eQTL_Coloc_Hit {tissue: STRING, omic: STRING}
pQTL_Coloc_Hit {tissue: STRING, omic: STRING}
SC_Expression {Symbol: STRING, single_cell: STRING}
Structure {Structure_available: BOOLEAN}
Protein_type {Protein class: STRING, Protein_type: STRING}
Relationship properties:
HAS_RISK_SCORE {available: INTEGER, Source: STRING}
HAS_ADDITIONAL_INFO {comment_type: STRING}
HAS_PROTEOMIC_DATA {log2_change: FLOAT, pvalue: FLOAT, padj: FLOAT}
Omicsynth_SMR_INFO {b_smr: FLOAT, p_smr: FLOAT}
pQTL_SMR_INFO {b_smr: FLOAT, p_smr: FLOAT}
eqTL_COLOC_INFO {posterior_probability: FLOAT, SNPs: STRING}
pQTL_COLOC_INFO {posterior_probability: FLOAT, HLA: BOOLEAN, cis_trans: BOOLEAN}
SC_DATA {log2_change: FLOAT, pvalue: STRING, padj: FLOAT}
The relationships:
(:Gene)-[:HAS_ENTREZ_ID]->(:Entrez)
(:Gene)-[:HAS_RISK_SCORE]->(:Risk_Score)
(:Gene)-[:HAS_GWAS_HIT]->(:GWAS)
(:Gene)-[:IS_DRUGGABLE]->(:Druggability)
(:Gene)-[:HAS_OMICSYNTH_SMR_HIT]->(:OmicSynth_SMR)
(:Gene)-[:CODES]->(:Protein)
(:Gene)-[:BELONGS_TO_CLASS]->(:Protein_Class)
(:Gene)-[:HAS_ONTOLOGY]->(:Gene_Ontology)
(:Gene)-[:INVOLVED_IN_PATHWAY]->(:Pathway)
(:Gene)-[:HAS_pQTL_SMR_HIT]->(:pQTL_SMR)
(:Gene)-[:HAS_eQTL_COLOCALIZATION_HIT]->(:eQTL_Coloc_Tissue)
(:Gene)-[:HAS_pQTL_COLOCALIZATION_HIT]->(:pQTL_Colocalization)
(:Protein)-[:HAS_3D_STRUCTURE]->(:Structure)
(:Protein)-[:IS_TYPE]->(:Protein_type)
(:Protein)-[:HAS_ADDITIONAL_INFO]->(:Comment)
(:Protein)-[:HAS_PROTEOMIC_DATA]->(:Cell)
(:Entrez)-[:ASSOCIATED_WITH_DISEASE]->(:Disease)
(:Entrez)-[:HAS_PHENOTYPE_ONTOLOGY]->(:Phenotype_Ontology)
(:Entrez)-[:ASSOCIATED_WITH_RARE_DISEASE]->(:Disease_Rare_source)
(:eQTL_Coloc_Tissue)-[:eqTL_COLOC_INFO]->(:eQTL_Coloc_Hit)
(:pQTL_Colocalization)-[:pQTL_COLOC_INFO]->(:pQTL_Coloc_Hit)
(:pQTL_SMR)-[:pQTL_SMR_INFO]->(:pQTL_SMR_HIT)
(:GWAS)-[:GWAS_INFO]->(:GWAS_HIT)
(:OmicSynth_SMR)-[:Omicsynth_SMR_INFO]->(:Omicsynth_SMR_HIT)
(:SC_Expression)-[:SC_DATA]->(:Cell)
"""
