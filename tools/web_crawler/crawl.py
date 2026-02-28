from trafilatura import extract

#TODO 
# - get the job step 
# - Find relavent osha pages - bing search api??
# - Fetch and extract text from the page - trafilatura
# - RAG - chunk the text, then rank chunks against the job step
# - Generate mitigations - write mitigations using the keyword and extracted data
# - out put in a way that can go into each jinja peice

#this is a list of job steps
jobstep = [] # this pull from the endpoint that gets all the jobsteps

construction_hazards = [
    # Struck-by / Caught-in / Equipment Hazards
    "struck_by_heavy_equipment",
    "struck_by_moving_vehicle",
    "struck_by_flying_debris",
    "struck_by_falling_object",
    "caught_in_between_equipment",
    "caught_between_materials",
    "caught_in_rotating_parts",
    "pinch_point_injury",
    "equipment_rollover",
    "crushed_by_load",
    "swing_radius_strike",
    "backover_incident",
    "blind_spot_exposure",
    "equipment_collision",
    "unsecured_load_shift",
    "rigging_failure",
    "dropped_load",
    "forklift_tip_over",
    "crane_boom_contact",

    # Excavation & Trenching
    "excavation_cave_in",
    "trench_collapse",
    "engulfment",
    "fall_into_excavation",
    "spoils_pile_failure",
    "undermined_structure",
    "inadequate_shoring",
    "improper_sloping",
    "inadequate_egress",
    "underground_utility_strike",
    "gas_line_strike",
    "water_line_break",
    "fiber_optic_damage",

    # Electrical
    "electrical_shock",
    "arc_flash",
    "arc_blast",
    "energized_line_contact",
    "overhead_powerline_contact",
    "damaged_extension_cord",
    "improper_grounding",
    "gfc_failure",
    "temporary_power_hazard",
    "static_discharge",

    # Slips / Trips / Falls
    "slip_on_wet_surface",
    "trip_over_material",
    "fall_from_height",
    "fall_same_level",
    "ladder_fall",
    "scaffold_fall",
    "unprotected_edge_fall",
    "roof_fall",
    "fall_through_opening",
    "uneven_ground_trip",
    "mud_ice_slip",
    "improper_three_point_contact",

    # Manual Handling / Ergonomic
    "overexertion",
    "improper_lifting",
    "repetitive_motion_injury",
    "muscle_strain",
    "back_injury",
    "awkward_posture",
    "twisting_while_lifting",
    "shoulder_strain",
    "hand_wrist_strain",
    "vibration_exposure",

    # Noise
    "high_noise_exposure",
    "sudden_impact_noise",
    "long_term_hearing_loss",
    "inadequate_hearing_protection",

    # Thermal Stress
    "heat_stress",
    "heat_exhaustion",
    "heat_stroke",
    "dehydration",
    "cold_stress",
    "hypothermia",
    "frostbite",
    "wind_chill_exposure",

    # Fire & Explosion
    "fuel_spill",
    "flammable_vapor_ignition",
    "hot_work_fire",
    "welding_spark_ignition",
    "explosive_gas_accumulation",
    "improper_refueling",
    "battery_explosion",
    "compressed_gas_cylinder_failure",
    "dust_explosion",

    # Chemical & Environmental
    "silica_exposure",
    "asbestos_exposure",
    "lead_exposure",
    "contaminated_soil_exposure",
    "radiological_exposure",
    "toxic_fume_inhalation",
    "diesel_exhaust_exposure",
    "confined_space_atmosphere",
    "oxygen_deficiency",
    "hazardous_material_spill",
    "chemical_burn",
    "eye_irritation_from_dust",
    "skin_contact_with_chemicals",

    # Hand & Power Tools
    "tool_kickback",
    "unguarded_blade_contact",
    "saw_cut_injury",
    "grinder_wheel_failure",
    "tool_overheating",
    "air_hose_whip",
    "improper_tool_use",
    "damaged_tool_use",
    "battery_tool_fire",

    # Vehicles & Traffic
    "vehicle_collision",
    "public_traffic_intrusion",
    "improper_traffic_control",
    "seatbelt_not_used",
    "fatigued_driving",
    "adverse_weather_driving",
    "poor_visibility_driving",

    # Lifting & Hoisting
    "overloaded_crane",
    "improper_rigging",
    "tagline_not_used",
    "load_swing",
    "boom_overextension",
    "lifting_unknown_weight",
    "person_under_suspended_load",
    "improper_hand_signal",

    # Weather & Environmental Conditions
    "lightning_strike",
    "high_wind_exposure",
    "heavy_rain_flooding",
    "snow_ice_accumulation",
    "extreme_heat_exposure",
    "extreme_cold_exposure",
    "poor_air_quality",
    "reduced_visibility_conditions",

    # Confined Space
    "confined_space_entry",
    "toxic_atmosphere",
    "hazardous_vapor_accumulation",
    "engulfment_in_confined_space",
    "restricted_exit_access",

    # Structural & Material Handling
    "structural_instability",
    "premature_formwork_removal",
    "improper_material_storage",
    "stacked_material_collapse",
    "rebar_impalement",
    "sharp_edge_contact",
    "glass_breakage",
    "formwork_failure",

    # Biological
    "insect_sting",
    "animal_encounter",
    "biohazard_exposure",
    "mold_exposure",

    # Laser & Specialty Equipment
    "laser_eye_exposure",
    "improper_laser_class_use",
    "survey_equipment_trip",

    # Compaction & Heavy Vibration
    "foot_crush_injury",
    "jumping_jack_instability",
    "ground_vibration_exposure",

    # Administrative / Human Factors
    "lack_of_training",
    "inadequate_supervision",
    "fatigue_related_error",
    "poor_communication",
    "improper_pre_task_planning",
    "failure_to_follow_procedure",
    "inadequate_ppe_use",
    "complacency",
    "rushed_work_activity"
]



