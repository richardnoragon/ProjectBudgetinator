import tkinter as tk
from tkinter import ttk

class EditPartnerDialog(tk.Toplevel):
    def __init__(self, parent, partner_number, partner_acronym, initial_values=None):
        super().__init__(parent)
        self.title(f"Edit Partner {partner_number}")
        self.result = None
        
        # Store the values
        self.partner_number = partner_number
        self.partner_acronym = partner_acronym
        self.initial_values = initial_values or {}
        
        # Create variables dictionary
        self.vars = {}
        
        # Create the form
        self._create_widgets()
        self._load_initial_values()
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Position the window
        self.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))

    def _create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Partner info section
        info_frame = ttk.LabelFrame(main_frame, text="Partner Information", padding="5")
        info_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        # Partner Number and Acronym (read-only)
        ttk.Label(info_frame, text="Partner Number and Acronym:").grid(row=0, column=0, sticky="w")
        partner_label = ttk.Label(info_frame, text=f"{self.partner_number}, {self.partner_acronym}")
        partner_label.grid(row=0, column=1, sticky="w")

        # Basic Information
        basic_frame = ttk.LabelFrame(main_frame, text="Basic Information", padding="5")
        basic_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5))

        fields = [
            ("Partner ID Code:", "partner_identification_code"),
            ("Name of Beneficiary:", "name_of_beneficiary"),
            ("Country:", "country"),
            ("Role:", "role"),
        ]

        for i, (label, var_name) in enumerate(fields):
            ttk.Label(basic_frame, text=label).grid(row=i, column=0, sticky="w", pady=2)
            self.vars[var_name] = tk.StringVar()
            ttk.Entry(basic_frame, textvariable=self.vars[var_name]).grid(
                row=i, column=1, sticky="ew", pady=2, padx=5
            )

        # Work Packages
        wp_frame = ttk.LabelFrame(main_frame, text="Work Packages", padding="5")
        wp_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=10)

        # Create WP entries (3 columns)
        for i in range(1, 16):
            col = (i-1) % 3
            row = (i-1) // 3
            ttk.Label(wp_frame, text=f"WP{i}:").grid(row=row, column=col*2, sticky="w", pady=2, padx=(5 if col else 0, 0))
            self.vars[f'wp{i}'] = tk.StringVar()
            ttk.Entry(wp_frame, textvariable=self.vars[f'wp{i}'], width=15).grid(
                row=row, column=col*2+1, sticky="w", pady=2, padx=5
            )

        # Subcontractors
        subcontract_frame = ttk.LabelFrame(main_frame, text="Subcontractors", padding="5")
        subcontract_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(0, 10))

        subcontract_fields = [
            ("Name Subcontractor 1:", "name_subcontractor_1"),
            ("Sum Subcontractor 1:", "sum_subcontractor_1"),
            ("Explanation Subcontractor 1:", "explanation_subcontractor_1"),
            ("Name Subcontractor 2:", "name_subcontractor_2"),
            ("Sum Subcontractor 2:", "sum_subcontractor_2"),
            ("Explanation Subcontractor 2:", "explanation_subcontractor_2"),
        ]

        for i, (label, var_name) in enumerate(subcontract_fields):
            ttk.Label(subcontract_frame, text=label).grid(row=i, column=0, sticky="w", pady=2)
            self.vars[var_name] = tk.StringVar()
            ttk.Entry(subcontract_frame, textvariable=self.vars[var_name]).grid(
                row=i, column=1, sticky="ew", pady=2, padx=5
            )

        # Financial Information
        finance_frame = ttk.LabelFrame(main_frame, text="Financial Information", padding="5")
        finance_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=(0, 10))

        finance_fields = [
            ("Sum Travel:", "sum_travel"),
            ("Sum Equipment:", "sum_equipment"),
            ("Sum Other:", "sum_other"),
            ("Sum Financial Support:", "sum_financial_support"),
            ("Sum Internal Goods:", "sum_internal_goods"),
            ("Sum Income Generated:", "sum_income_generated"),
            ("Sum Financial Contributions:", "sum_financial_contributions"),
            ("Sum Own Resources:", "sum_own_resources"),
        ]

        for i, (label, var_name) in enumerate(finance_fields):
            ttk.Label(finance_frame, text=label).grid(row=i, column=0, sticky="w", pady=2)
            self.vars[var_name] = tk.StringVar()
            ttk.Entry(finance_frame, textvariable=self.vars[var_name]).grid(
                row=i, column=1, sticky="ew", pady=2, padx=5
            )

        # Explanations
        explain_frame = ttk.LabelFrame(main_frame, text="Explanations", padding="5")
        explain_frame.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=(0, 10))

        explain_fields = [
            ("Financial Support:", "explanation_financial_support"),
            ("Internal Goods:", "explanation_internal_goods"),
            ("Income Generated:", "explanation_income_generated"),
            ("Financial Contributions:", "explanation_financial_contributions"),
            ("Own Resources:", "explanation_own_resources"),
        ]

        for i, (label, var_name) in enumerate(explain_fields):
            ttk.Label(explain_frame, text=label).grid(row=i, column=0, sticky="w", pady=2)
            self.vars[var_name] = tk.StringVar()
            ttk.Entry(explain_frame, textvariable=self.vars[var_name]).grid(
                row=i, column=1, sticky="ew", pady=2, padx=5
            )

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Save", command=self._on_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(side=tk.LEFT, padx=5)

        # Configure grid weights
        self.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        for frame in [basic_frame, wp_frame, subcontract_frame, finance_frame, explain_frame]:
            frame.grid_columnconfigure(1, weight=1)

    def _load_initial_values(self):
        """Load the initial values into the form fields."""
        for key, value in self.initial_values.items():
            if key in self.vars:
                self.vars[key].set(str(value) if value is not None else '')

    def _on_save(self):
        """Save the form data and close the dialog."""
        self.result = {key: var.get() for key, var in self.vars.items()}
        self.result['project_partner_number'] = self.partner_number
        self.result['partner_acronym'] = self.partner_acronym
        self.destroy()

    def _on_cancel(self):
        """Cancel the edit and close the dialog."""
        self.result = None
        self.destroy()
