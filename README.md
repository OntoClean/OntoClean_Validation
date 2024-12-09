# OntoClean Validation

This repository contains the prompts, scripts, and some results from a research study focused on the **OntoClean criteria verification using LLM (GPT_4)**. The study leverages GPT-4 to label terms based on **rigidity**, **identity**, and **unity** criteria.

## Contents
1. [Introduction](#introduction)
2. [Files](#files)
3. [How to Use](#how-to-use)
4. [References](#references)

---

## Introduction

The research applies the OntoClean methodology to evaluate and validate ontological categories. The repository includes:
- Scripts for data processing and validation for meta property labelling.
- Prompts and templates for GPT-4 interactions.
- Results comparing GPT-4 outcomes with literature-based findings for Idenity/Unity Criterion Generaion.

---

## Files

### 1. **`GPT_4VsLiterature.md`**
- **Description:** Provides a detailed comparison of GPT-4 outcomes against literature for subsumption relationship verification.
- **Includes:**
  - Identity criteria for concepts such as Chemical Entities, Macromolecules, Micronutrients, etc based on literture (ground-truth information).
  - GPT-4 generated outcomes for these concepts.
    Using BERT sematic similarity measurement similiarity of maning of the content has been discussed in the paper
- **References:** Literature citations such as CHEBI Database and FoodB [1].

### 2. **`Identity_Unity_Criterion_Generation.txt`**
- **Description:** Contains the prompt templates for generating identity and unity criteria.
- **Includes:**
  - Identity prompt template.
  - Unity prompt template.

### 3. **`Meta_properties_extraction.py`**
- **Description:** Python script for automating meta-property classification using GPT-4.
- **Features:**
  - Prompts GPT-4 to classify terms based on rigidity, identity, and unity.
  - Refines GPT-4 responses for accuracy.
  - Outputs results in a structured CSV file.

### 4. **`README.md`**
- **Description:** Current file, providing an overview of the repository.

---

## How to Use

### Prerequisites
1. Python 3.x
2. Required libraries: `pandas`, `openai`, `nltk`
   ```bash
   pip install pandas openai nltk
