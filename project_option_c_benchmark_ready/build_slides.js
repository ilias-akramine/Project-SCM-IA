const pptxgen = require('pptxgenjs');
const { imageSizingContain, imageSizingCrop } = require('/home/oai/skills/slides/pptxgenjs_helpers');
const path = require('path');
const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'OpenAI';
pptx.subject = 'Option C VRPTW';
pptx.title = 'Dynamic Routing VRPTW';
pptx.company = 'OpenAI';
pptx.lang = 'en-US';
themeColor = '17365D';
light = 'EAF1FB';

const root = '/mnt/data/project_option_c_refined';
const fig = path.join(root, 'figures');

function title(slide, t, s) {
  slide.addText(t, { x:0.5, y:0.3, w:12.2, h:0.45, fontFace:'Aptos', fontSize:24, bold:true, color:themeColor });
  if (s) slide.addText(s, { x:0.5, y:0.78, w:12.0, h:0.28, fontFace:'Aptos', fontSize:10.5, color:'4F6177' });
  slide.addShape(pptx.ShapeType.line, { x:0.5, y:1.08, w:12.0, h:0, line:{ color:'9DB2CE', pt:1.2 } });
}
function bulletSlide(slide, header, bullets) {
  title(slide, header);
  let y = 1.35;
  bullets.forEach(b => {
    slide.addShape(pptx.ShapeType.roundRect, { x:0.6, y:y+0.03, w:0.16, h:0.16, radius:0.03, fill:{color:'5B9BD5'}, line:{color:'5B9BD5'} });
    slide.addText(b, { x:0.9, y, w:11.6, h:0.45, fontSize:18, color:'1F1F1F', breakLine:false, fontFace:'Aptos' });
    y += 0.62;
  });
}

let s = pptx.addSlide();
title(s, 'Option C - Dynamic Routing VRPTW', 'Full Python project with OR-Tools, Simulated Annealing, KPIs, and dynamic re-routing');
s.addText('Problem covered', { x:0.7, y:1.5, w:3.2, h:0.3, fontSize:20, bold:true, color:themeColor });
s.addText('• VRPTW\n• Real-time re-routing\n• New urgent order\n• Traffic incident', { x:0.9, y:1.95, w:3.1, h:2.0, fontSize:18, breakLine:true });
s.addText('Deliverables', { x:4.6, y:1.5, w:3.2, h:0.3, fontSize:20, bold:true, color:themeColor });
s.addText('• Python code only in /code\n• Benchmark comparison C1 / R1 / RC1\n• KPI charts and route maps\n• IEEE-style PDF report\n• Slides presentation', { x:4.8, y:1.95, w:4.2, h:2.2, fontSize:18, breakLine:true });
s.addText('Methods', { x:9.2, y:1.5, w:2.4, h:0.3, fontSize:20, bold:true, color:themeColor });
s.addText('• OR-Tools\n• Simulated Annealing\n• Greedy baseline', { x:9.4, y:1.95, w:2.8, h:1.5, fontSize:18, breakLine:true });

s = pptx.addSlide();
bulletSlide(s, 'Methodology kept simple and solid', [
  'OR-Tools is the main solver for VRPTW with time windows and vehicle capacity.',
  'A greedy baseline is used as a reference to show the gain from optimization.',
  'Simulated Annealing is the comparison metaheuristic: swap, insert, reverse, accept or reject with temperature.',
  'Dynamic scenario = one urgent order + one traffic zone that inflates travel times.'
]);

s = pptx.addSlide();
title(s, 'Benchmark comparison on C1, R1 and RC1', 'KPIs: total distance, vehicles used, time-window respect, estimated CO2');
s.addImage({ path: path.join(fig, 'comparison_table.png'), ...imageSizingContain(path.join(fig, 'comparison_table.png'), 0.55, 1.45, 12.1, 2.05) });
s.addImage({ path: path.join(fig, 'dashboard.png'), ...imageSizingContain(path.join(fig, 'dashboard.png'), 0.7, 3.7, 11.8, 3.1) });

s = pptx.addSlide();
title(s, 'Initial optimized routes (RC1)');
s.addImage({ path: path.join(fig, 'initial_routes.png'), ...imageSizingContain(path.join(fig, 'initial_routes.png'), 0.6, 1.35, 12.0, 5.7) });

s = pptx.addSlide();
title(s, 'Dynamic re-routing after urgent order + traffic');
s.addImage({ path: path.join(fig, 'rerouted_routes.png'), ...imageSizingContain(path.join(fig, 'rerouted_routes.png'), 0.55, 1.35, 8.2, 5.5) });
s.addImage({ path: path.join(fig, 'dynamic_impact.png'), ...imageSizingContain(path.join(fig, 'dynamic_impact.png'), 8.95, 1.75, 3.2, 3.6) });
s.addText('Main takeaway:\nThe fleet uses one more vehicle after the disruption, and the total distance increases significantly, which confirms the impact of dynamic events on routing.', { x:8.95, y:5.6, w:3.2, h:1.0, fontSize:14, color:'1F1F1F' });

s = pptx.addSlide();
bulletSlide(s, 'Interpretation', [
  'OR-Tools consistently beats the baseline and slightly outperforms the metaheuristic on total distance.',
  'The metaheuristic remains acceptable as a custom comparison method and is easy to explain in an oral defense.',
  'The project now clearly covers: VRPTW, dynamic re-routing, new orders, incidents, KPIs, and benchmark instances.',
  'Everything is kept in Python in the code folder, ready for GitHub submission.'
]);

pptx.writeFile({ fileName: path.join(root, 'slides_presentation.pptx') });
