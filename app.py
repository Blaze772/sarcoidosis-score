from flask import Flask, render_template, request, redirect, url_for, session
app = Flask(__name__)
app.secret_key = "sarcoidosis-scoring-key-2024"  # ← add this line

@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# All organ systems and findings
organ_systems = {
    "Lungs": {
        "high": {
            "lungs_bilateral_hilar_adenopathy": {
                "label": "CXR: Bilateral hilar adenopathy",
                "points": 3
            },
            "lungs_perilymphatic_nodules": {
                "label": "Chest CT: Peri-lymphatic nodules",
                "points": 3
            },
            "lungs_symmetrical_hilar_mediastinal_adenopathy": {
                "label": "Chest CT: Symmetrical hilar/mediastinal adenopathy",
                "points": 3
            },
            "lungs_mediastinal_hilar_enhancement": {
                "label": "PET/Gallium-67: Mediastinal/hilar enhancement",
                "points": 3
            },
        },
        "mid": {
            "lungs_diffuse_infiltrates": {
                "label": "CXR: Diffuse infiltrates",
                "points": 2
            },
            "lungs_upper_lobe_fibrosis": {
                "label": "CXR: Upper lobe fibrosis",
                "points": 2
            },
            "lungs_peribronchial_thickening": {
                "label": "Chest CT: Peri-bronchial thickening",
                "points": 2
            },
            "lungs_bal_lymphocytic_alveolitis": {
                "label": "BAL: Lymphocytic alveolitis",
                "points": 2
            },
            "lungs_bal_cd4_cd8_ratio": {
                "label": "BAL: Elevated CD4/CD8 ratio",
                "points": 2
            },
            "lungs_diffuse_parenchymal_lung_enhancement": {
                "label": "PET/Gallium-67: Diffuse parenchymal lung enhancement",
                "points": 2
            },
            "lungs_tbna_lymphoid_aggregates": {
                "label": "TBNA: Lymphoid aggregates/giant cells",
                "points": 2
            },
        }
    },

    "Brain/Nerve": {
        "high": {
            "brain_nerve_granulomatous_neuro_syndrome": {
                "label": "Clinical syndrome consistent with granulomatous inflammation of the neurologic system",
                "points": 3
            },
        },
        "mid": {
            "brain_nerve_isolated_facial_palsy_negative_mri": {
                "label": "Isolated facial palsy, negative MRI",
                "points": 2
            },
            "brain_nerve_consistent_clinical_syndrome": {
                "label": "Clinical syndrome consistent with granulomatous inflammation",
                "points": 2
            },
        }
    },

    "Skin": {
        "high": {
            "skin_lupus_pernio": {
                "label": "Lupus pernio",
                "points": 3
            },
        },
        "mid": {}
    },

    "Eyes": {
        "high": {
            "eyes_uveitis": {
                "label": "Uveitis",
                "points": 3
            },
            "eyes_optic_neuritis": {
                "label": "Optic neuritis",
                "points": 3
            },
            "eyes_mutton_fat_keratic_precipitates": {
                "label": "Mutton fat keratic precipitates",
                "points": 3
            },
            "eyes_iris_nodule": {
                "label": "Iris nodule",
                "points": 3
            },
            "eyes_snowball_string_of_pearls": {
                "label": "Snowball/string of pearls (pars planitis)",
                "points": 3
            },
        },
        "mid": {
            "eyes_lacrimal_gland_swelling": {
                "label": "Lacrimal gland swelling",
                "points": 2
            },
            "eyes_trabecular_meshwork_nodules": {
                "label": "Trabecular meshwork nodules",
                "points": 2
            },
            "eyes_retinitis": {
                "label": "Retinitis",
                "points": 2
            },
            "eyes_scleritis": {
                "label": "Scleritis",
                "points": 2
            },
            "eyes_multiple_chorioretinal_lesions": {
                "label": "Multiple chorioretinal peripheral lesions",
                "points": 2
            },
            "eyes_adnexal_nodularity": {
                "label": "Adnexal nodularity",
                "points": 2
            },
            "eyes_candle_wax_drippings": {
                "label": "Candle wax drippings",
                "points": 2
            },
        }
    },

    "Bone Marrow": {
        "high": {
            "bone_marrow_diffuse_pet_uptake": {
                "label": "PET displaying diffuse uptake",
                "points": 3
            },
        },
        "mid": {}
    },

    "Spleen": {
        "high": {
            "spleen_low_attenuation_nodules_ct": {
                "label": "Low attenuation nodules on CT",
                "points": 3
            },
            "spleen_pet_gallium_uptake_nodules": {
                "label": "PET/Gallium-67 uptake in splenic nodules",
                "points": 3
            },
            "spleen_splenomegaly": {
                "label": "Splenomegaly on imaging or physical examination",
                "points": 3
            },
        },
        "mid": {}
    },

    "Bone": {
        "high": {
            "bone_typical_radiographic_features": {
                "label": "Typical radiographic features (trabecular pattern, osteolysis, cysts/punched out lesions)",
                "points": 3
            },
        },
        "mid": {
            "bone_dactylitis": {
                "label": "Dactylitis",
                "points": 2
            },
            "bone_nodular_tenosynovitis": {
                "label": "Nodular tenosynovitis",
                "points": 2
            },
            "bone_positive_pet_mri_gallium": {
                "label": "Positive PET, MRI, or Gallium-67",
                "points": 2
            },
        }
    },

    "Parotid/Salivary Glands": {
        "high": {
            "parotid_positive_gallium_panda": {
                "label": 'Positive Gallium-67 scan ("Panda")',
                "points": 3
            },
            "parotid_positive_pet_parotids": {
                "label": "Positive PET scan of parotids",
                "points": 3
            },
        },
        "mid": {
            "parotid_symmetrical_parotitis_mumps": {
                "label": "Symmetrical parotitis with syndrome of mumps",
                "points": 2
            },
            "parotid_enlarged_salivary_glands": {
                "label": "Enlarged salivary glands",
                "points": 2
            },
        }
    },

    "Endocrine": {
        "high": {
            "endocrine_hypercalcemia_hypercalciuria": {
                "label": "Hypercalcemia or hypercalciuria plus all of the following: a normal serum PTH level, a normal or increased 1,25-OH dihydroxy vitamin D level, and a low 25-OH vitamin D level",
                "points": 3
            },
        },
        "mid": {
            "endocrine_nephrolithiasis_pattern": {
                "label": "Nephrolithiasis plus all of the following: a normal serum PTH level, a normal or increased 1,25-OH vitamin D level, and a low 25-OH vitamin D level",
                "points": 2
            },
        }
    },

    "Ear/Nose/Throat": {
        "high": {
            "ent_granulomatous_laryngoscopy": {
                "label": "Granulomatous changes on direct laryngoscopy",
                "points": 3
            },
        },
        "mid": {
            "ent_consistent_imaging": {
                "label": "Consistent imaging studies (eg, sinonasal erosion, mucoperiosteal thickening, positive PET scan)",
                "points": 2
            },
        }
    },

    "Heart": {
        "high": {
            "heart_treatment_responsive_cardiomyopathy": {
                "label": "Treatment responsive cardiomyopathy",
                "points": 3
            },
            "heart_av_nodal_blockade": {
                "label": "AV-nodal blockade",
                "points": 3
            },
        },
        "mid": {}
    },

    "Muscles": {
        "high": {
            "muscles_positive_imaging": {
                "label": "Positive imaging (MRI, Gallium-67)",
                "points": 3
            },
            "muscles_palpable_masses": {
                "label": "Palpable muscle masses",
                "points": 3
            },
        },
        "mid": {}
    },

    "Kidney": {
        "high": {
            "kidney_treatment_responsive_renal_failure": {
                "label": "Treatment-responsive renal failure without alternative diagnosis",
                "points": 3
            },
        },
        "mid": {}
    },

    "Nonthoracic Lymph Nodes": {
        "high": {
            "lymph_multiple_palpable_nodes": {
                "label": "Multiple enlarged palpable cervical or epitrochlear lymph nodes without B symptoms",
                "points": 3
            },
        },
        "mid": {
            "lymph_two_or_more_stations": {
                "label": "Enlarged lymph nodes identified by imaging in at least 2 peripheral or visceral lymph node stations without B symptoms",
                "points": 2
            },
        }
    },

    "Liver": {
        "high": {
            "liver_hepatomegaly": {
                "label": "Abdominal imaging demonstrating hepatomegaly",
                "points": 3
            },
            "liver_hepatic_nodules": {
                "label": "Abdominal imaging demonstrating hepatic nodules",
                "points": 3
            },
            "liver_alkaline_phosphatase": {
                "label": "Alkaline phosphatase > 3 times ULN",
                "points": 3
            },
        },
        "mid": {}
    },
}


def calculate_score(selected):
    total = 0
    selected_findings = []

    for organ_name, organ_data in organ_systems.items():
        for probability_level in organ_data.values():
            for key, item in probability_level.items():
                if key in selected:
                    total += item["points"]
                    selected_findings.append({
                        "organ": organ_name,
                        "label": item["label"],
                        "points": item["points"]
                    })

    return total, selected_findings


def interpret(score):
    if score >= 12:
        return "High likelihood of sarcoidosis"
    elif score >= 8:
        return "Moderate likelihood of sarcoidosis"
    elif score >= 4:
        return "Low likelihood — consider further testing"
    else:
        return "Unlikely sarcoidosis"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        selected = request.form.getlist("symptoms")
        score, selected_findings = calculate_score(selected)
        result = interpret(score)
        # Store in session then redirect to GET
        session["score"] = score
        session["result"] = result
        session["selected"] = selected
        session["selected_findings"] = selected_findings
        return redirect(url_for("index"))

    # GET request — pull from session if available
    score = session.pop("score", 0)
    result = session.pop("result", None)
    selected = session.pop("selected", [])
    selected_findings = session.pop("selected_findings", [])
    has_calculated = result is not None

    return render_template(
        "index.html",
        organ_systems=organ_systems,
        score=score,
        result=result,
        selected=selected,
        selected_findings=selected_findings,
        has_calculated=has_calculated
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

