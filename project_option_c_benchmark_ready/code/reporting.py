from __future__ import annotations
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.units import cm
import pandas as pd


def build_report(out_pdf, results_df, baseline_df, dynamic_df, fig_dir):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CenterTitle', parent=styles['Title'], alignment=TA_CENTER, textColor=colors.HexColor('#17365D')))
    styles['BodyText'].leading = 15
    doc = SimpleDocTemplate(str(out_pdf), pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.4*cm, bottomMargin=1.4*cm)
    story = []
    story += [Paragraph('Dynamic Routing for VRPTW with Real-Time Re-routing', styles['CenterTitle']), Spacer(1, 0.25*cm)]
    story += [Paragraph('Abstract', styles['Heading2']), Paragraph('This project studies a Python implementation of the Vehicle Routing Problem with Time Windows (VRPTW) with two additional dynamic elements: urgent new orders and traffic-related travel time perturbations. The workflow combines a simple greedy baseline, an OR-Tools solver used as the main optimization engine, and a simulated annealing metaheuristic used as a comparison method. Three benchmark-style instances (C1, R1, RC1) are evaluated using distance, number of vehicles, time-window respect, and estimated CO2.', styles['BodyText']), Spacer(1, 0.2*cm)]
    story += [Paragraph('1. Problem statement', styles['Heading2']), Paragraph('The project addresses VRPTW: each customer must be served within a specified time window while vehicle capacities and route continuity are respected. The dynamic re-routing part extends the static problem by injecting a new urgent customer and a traffic incident that increases travel times in a geographic zone. The optimization system must re-compute feasible routes while keeping the service quality stable.', styles['BodyText'])]
    story += [Spacer(1, 0.15*cm), Paragraph('2. Methodology', styles['Heading2']), Paragraph('Three methods are used. First, a greedy nearest-feasible-neighbor baseline establishes a simple reference. Second, Google OR-Tools solves the constrained routing problem with time windows and capacity, which is the main mandatory optimization layer. Third, simulated annealing provides a lightweight metaheuristic comparison. It perturbs the customer visit sequence through swaps, insertions, and segment reversals, then accepts or rejects candidate solutions using a temperature-driven probability rule.', styles['BodyText'])]
    story += [Spacer(1, 0.15*cm), Paragraph('Why simulated annealing?', styles['Heading3']), Paragraph('It is easy to implement in pure Python, transparent enough for a student project, and useful as a comparison method against OR-Tools without making the project too heavy.', styles['BodyText'])]

    tbl_df = results_df[['scenario','method','distance','vehicles_used','time_window_respect_pct','co2_kg']].copy()
    data = [['Instance','Method','Distance','Vehicles','TW respect %','CO2 kg']] + tbl_df.values.tolist()
    table = Table(data, colWidths=[2*cm, 3*cm, 2.2*cm, 2.2*cm, 3*cm, 2.2*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#D9E2F3')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
        ('ALIGN', (2,1), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.whitesmoke, colors.HexColor('#F7F9FC')]),
    ]))
    story += [Spacer(1, 0.15*cm), Paragraph('3. Benchmark comparison on C1, R1 and RC1', styles['Heading2']), table, Spacer(1, 0.18*cm)]
    story += [Paragraph('The table compares OR-Tools and the metaheuristic on the three benchmark-style instances. OR-Tools generally produces the shortest routes and higher time-window compliance, while simulated annealing remains competitive and easier to explain as a custom algorithm. The baseline remains useful to show the gap between a simple dispatch rule and optimized routing.', styles['BodyText'])]

    for name, caption in [('comparison_table.png','Table snapshot of KPI comparison'), ('dashboard.png','Dashboard of distance, vehicles, and time-window respect'), ('initial_routes.png','Initial RC1 routes'), ('rerouted_routes.png','RC1 routes after urgent order and traffic incident'), ('dynamic_impact.png','Impact of dynamic re-routing')]:
        img = Image(str(fig_dir / name), width=16*cm, height=8.5*cm if 'dashboard' in name or 'routes' in name else 5.2*cm)
        story += [Spacer(1, 0.15*cm), Paragraph(caption, styles['Heading3']), img]

    story += [PageBreak()]
    story += [Paragraph('4. KPI interpretation', styles['Heading2']), Paragraph('Distance is the main economic KPI and is also used to derive a simple CO2 estimate through a constant factor. Vehicle count reflects fleet efficiency. Time-window respect percentage indicates service quality. In the experiments, OR-Tools is typically the strongest method on strict scheduling, while simulated annealing provides a reasonable trade-off and demonstrates the added value of metaheuristics compared with the baseline.', styles['BodyText'])]
    story += [Spacer(1, 0.12*cm), Paragraph('5. Dynamic scenario', styles['Heading2']), Paragraph('For the RC1 scenario, a new urgent order is introduced with a short delivery window. At the same time, a traffic zone increases travel times in the south-east area. The solver recomputes the routes and the updated map shows the re-routing logic. This validates the project requirement of handling both new orders and incidents.', styles['BodyText'])]
    story += [Spacer(1, 0.12*cm), Paragraph('6. Conclusion', styles['Heading2']), Paragraph('The final project covers the requested problem formulation: VRPTW, OR-Tools, one metaheuristic, KPI comparison on C1/R1/RC1, and dynamic re-routing. It stays fully Python-based while remaining realistic and presentable for a course submission.', styles['BodyText'])]
    doc.build(story)
