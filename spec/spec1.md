# Irish Children’s Triage System (ICTS) - Specification

## Overview

A Java-based  application that digitizes the National Emergency Medicine Programme Irish Children’s Triage System (ICTS). It parses PDF guidelines to generate executable business rules and provides a user-friendly GUI for triaging patients.

**Purpose:** Automate the triage process using rule-based logic derived directly from official medical guidelines, assisting healthcare professionals in determining clinical priority.

---

## What Users Can Do

1.  **Generate Rules:** Parse the official ICTS PDF to create executable Drools rules.
2.  **Simulate Triage:** Input a patient's age and symptoms.
3.  **Select Symptoms:** Choose from a dynamic list of symptoms extracted from the guidelines.
4.  **View Results:** Instantly see the Triage Category (Colour) and Priority.

---

## User Interface

### Layout Mockup


**Tab 1: Setup**
```
┌─────────────────────────────────────────┐
│  Setup  │  Triage Simulation            │
│                                         │
│  [ Generate Rules from PDF ]            │
│                                         │
│  Status: Rules Generated Successfully.  │
│                                         │
└─────────────────────────────────────────┘
```

**Tab 2: Triage Simulation**
```
┌─────────────────────────────────────────┐
│  Setup  │  Triage Simulation            │
│                                         │
│  ┌─ Patient Details ─────────────────┐  │
│  │ Age: [ 10 ]                       │  │
│  │ Symptom: [ Airway compromise  ▼ ] │  │
│  │          [ Add Symptom ]          │  │
│  └───────────────────────────────────┘  │
│                                         │
│  Symptoms List:                         │
│  ┌───────────────────────────────────┐  │
│  │ - Airway compromise               │  │
│  │                                   │  │
│  └───────────────────────────────────┘  │
│                                         │
│  [ Clear Symptoms ]  [ Triage Patient ] │
│                                         │
│  Result: Red (Priority 1)               │
│                                         │
└─────────────────────────────────────────┘
```

**Initial Menu** 
1. Triage Patient
2. List Available Symptoms
3. Generate Rules from PDF
4. Exit


---

## Features

### Feature 1: Patient Triage

**Input:**
- **Age:** Numeric input for patient age.
- **Symptoms:** Dropdown selection populated dynamically from the generated rules. Users can add multiple symptoms.

**Behavior:**
- Engine matches patient data against 700+ generated rules.
- Determines the highest priority (lowest category number) triggered.
- If no specific rule matches, defaults to "Blue".

**Output:**
- **Triage Result:** Displayed as Text (e.g., "Red") and color-coded visually.

---

### Feature 2: Dynamic Symptom List

**Behavior:**
- Reads the generated DRL file.
- Extracts unique symptom names used in `Symptom( name == "..." )` patterns.
- Populates the symptom dropdown to ensure users can only select valid, rule-triggering symptoms.

---

### Feature 3: Rule Generation

**Input:**
- Source PDF file: `national-emergency-medicine-programme-irish-childrens-triage-system-icts.pdf`

**Behavior:**
- checks to see if the Drools (`.drl`) file already exists, and it has a new timestamp than the source pdf file. If it does, it skips the rule generation step.
- Parses text and coordinates to identify Flowcharts, Symptoms, and Categories.
- Generates a Drools (`.drl`) file containing executable rules.
- Updates the application state with the new rules.

**Output:**
- `generated_rules/triage.drl` file.
- Success/Error status message in the GUI.

---

## Technical Architecture

### Business Components

i.  **Data Model**:
    - `Patient`: Holds ID, Age, List of Symptoms.
    - `Symptom`: Wrapper for symptom strings.
    - `TriageResult`: Encapsulates Color and Priority.

### Core Components

1.  **User Interface (`Console')**:
    - Interface: simple console application.

2.  **PDF Parser (`TriageRuleGenerator`)**:
    - library: `Apache PDFBox`
    - Logic: Custom `PDFTextStripper` using X/Y coordinates to structure unstructured PDF content.
3.  **Rules Engine (`TriageEngine`)**:
    - Library: `Drools (Apache KIE)`
    - Logic: Stateful/Stateless session execution against the generated DRL.

4.  **Spring Framework**:
    - Use the Spring Boot framework to create a REST API for the application.
    - Use the Spring Boot framework to create a web application for the application.
    - Use the Spring Boot framework to create a command line interface for the application.
    - Use the Spring Boot framework to create a JAR file for the application.

6.  **Testing**:
    - Use Serenity for testing and create tests
    - Extract 3 scenarios 
    - write a script
    - 

7. **README.md**:
    - Provide a clear readme.md summarizing what the application does
    - Provide a clear readme.md file documenting the how to generate the rules and run the application Command line.
    - Provide a clear readme.md file documenting the how to run the tests
    - Describe the application structure and technical archicture.
    

---

## Success Criteria

**Test 1: Rule Generation**
- Click "Generate Rules".
- Verify success message.
- Verify `generated_rules/triage.drl` exists and contains ~761 rules.

**Test 2: High Priority Triage**
- Input Age: 5.
- Add Symptom: "Airway compromise".
- Click Triage.
- **Result:** RED (Priority 1).

**Test 3: Lower Priority Triage**
- Input Age: 8.
- Add Symptom: "Minor limb injury".
- Click Triage.
- **Result:** GREEN or BLUE (depending on specific rule match).

**Test 4: User interface Responsiveness**
- Verify dropdown is populated.
- Verify "Clear Symptoms" resets the list and result.

---

## API & Data

**Input Data Source:**
- PDF File located in `spec/` directory.

**Output Data:**
- Drools Rule File: Text-based DRL format.

**Rules Format:**
```drools
rule "Rule_1_FlowchartName"
    when
        $p : Patient( $s : symptoms )
        Symptom( name == "Specific Symptom" ) from $s
    then
        insert(new TriageResult("Red"));
end
```

---

## Technical Requirements

**Language:** Java 21
**Build System:** Maven
**Dependencies:**
- `org.drools:drools-core`
- `org.drools:drools-compiler`
- `org.drools:drools-mvel`
- `org.apache.pdfbox:pdfbox`
- `org.slf4j:slf4j-simple`

**Environment:** Desktop (Windows/Linux/macOS)
**Logging** slf4j-simple

## Read Only files in this project
Do not modify these files or folders
- any files in the `spec/` directory
- `sources.md` file
- `presentation.md` file
- `todo.md` file
- `versions.md` file

