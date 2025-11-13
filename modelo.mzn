% ================================================================
% MODELO OPTIMIZADO - PLANIFICACIÓN DE TURNOS (versión podada v2)
% - Compatible con 2 o 3 turnos por día
% - Heurística adaptativa (dom_w_deg)
% - Cortes anti-simetría (personas y días)
% - Cotas superiores ajustadas
% - Compatible con todas las versiones de MiniZinc / Chuffed
% ================================================================

int: horizonte_dias;
int: num_trabajadores;
set of int: PERSONAS = 1..num_trabajadores;
set of int: DIAS = 1..horizonte_dias;
set of int: TURNOS; % {1..2} o {1..3}
int: num_semanas;
set of int: SEMANAS = 1..num_semanas;

array[DIAS, TURNOS] of int: demanda;
array[PERSONAS, DIAS, TURNOS] of int: puntajes;

% ------------------------------------------------
% Parámetros derivados (para acotar búsqueda)
% ------------------------------------------------
int: demanda_total = sum(d in DIAS, t in TURNOS)(demanda[d,t]);
int: max_turnos_por_persona = ceil(demanda_total / num_trabajadores) + 1;

% ================================================================
% VARIABLES
% ================================================================
array[PERSONAS, DIAS, TURNOS] of var 0..1: x;
array[PERSONAS, SEMANAS] of var 0..1: y;

array[PERSONAS, DIAS] of var 0..2: turnos_dia =
  array2d(PERSONAS, DIAS, [sum(t in TURNOS)(x[p,d,t]) | p in PERSONAS, d in DIAS]);

array[PERSONAS, SEMANAS] of var 0..4: turnos_finde;

% ================================================================
% FUNCIÓN OBJETIVO + HEURÍSTICA DE BÚSQUEDA
% ================================================================
solve
  :: int_search(
      [x[p,d,t] | p in PERSONAS, d in DIAS, t in TURNOS] ++
      [y[p,w] | p in PERSONAS, w in SEMANAS],
      dom_w_deg,      % heurística adaptativa (alta poda)
      indomain_max
  )
  maximize sum(p in PERSONAS, d in DIAS, t in TURNOS)(
      puntajes[p,d,t] * x[p,d,t]
  );

% ================================================================
% RESTRICCIONES PRINCIPALES
% ================================================================
constraint forall(d in DIAS, t in TURNOS)(
  sum(p in PERSONAS)(x[p,d,t]) = demanda[d,t]
);

constraint forall(p in PERSONAS, d in DIAS, t in TURNOS)(
  puntajes[p,d,t] = 0 -> x[p,d,t] = 0
);

constraint forall(p in PERSONAS, d in DIAS)(
  sum(t in TURNOS)(x[p,d,t]) <= 2
);

constraint if max(TURNOS) >= 3 then
  forall(p in PERSONAS, d in 1..horizonte_dias-1)(
    x[p,d,max(TURNOS)] + x[p,d+1,min(TURNOS)] <= 1
  )
else
  true
endif;

function set of int: dias_finde_semana(int: semana) = 
  let {
    int: inicio_semana = (semana - 1) * 7 + 1,
    int: sabado = inicio_semana + 5,
    int: domingo = inicio_semana + 6
  } in
  {d | d in {sabado, domingo} where d <= horizonte_dias};

constraint forall(p in PERSONAS, w in SEMANAS)(
  y[p,w] = bool2int(sum(d in dias_finde_semana(w), t in TURNOS)(x[p,d,t]) > 0)
);

constraint if num_semanas >= 3 then
  forall(p in PERSONAS, w in 1..num_semanas-2)(
    y[p,w] + y[p,w+1] + y[p,w+2] <= 2
  )
else
  true
endif;

% ================================================================
% RESTRICCIONES DE PODA / ANTI-SIMETRÍA
% ================================================================
constraint forall(p in PERSONAS)(
  sum(d in DIAS, t in TURNOS)(x[p,d,t]) <= max_turnos_por_persona
);

constraint forall(p in 1..num_trabajadores-1)(
  sum(d in DIAS, t in TURNOS)(x[p,d,t]) >=
  sum(d in DIAS, t in TURNOS)(x[p+1,d,t])
);

constraint forall(d in 1..horizonte_dias-1)(
  sum(p in PERSONAS, t in TURNOS)(x[p,d,t]) <=
  sum(p in PERSONAS, t in TURNOS)(x[p,d+1,t])
);

% ================================================================
% SALIDA / OUTPUT
% ================================================================
int: cota_superior_objetivo =
  sum(d in DIAS, t in TURNOS)(
    max([if puntajes[p,d,t] > 0 then puntajes[p,d,t] else 0 endif | p in PERSONAS]) *
    demanda[d,t]
  );

output [
  "ASIGNACIÓN ÓPTIMA (o mejor conocida)\n",
  "Puntaje total: ", show(fix(sum(p in PERSONAS, d in DIAS, t in TURNOS)(
      puntajes[p,d,t] * x[p,d,t]))), " / ",
  show(cota_superior_objetivo), " (",
  show_int(3, fix(100 * sum(p in PERSONAS, d in DIAS, t in TURNOS)(
      puntajes[p,d,t] * x[p,d,t]) div cota_superior_objetivo)), "%)\n\n",
  "LEGENDA: " ++
  if card(TURNOS) = 2 then "D=Día, N=Noche\n\n"
  else "M=Mañana, T=Tarde, N=Noche\n\n" endif,
  "DÍA | " ++ join(" | ", ["P" ++ show(p) | p in PERSONAS]) ++ " | DEMANDA\n",
  "----+-" ++ join("--", ["-----------" | p in PERSONAS]) ++ "-+----------\n"
] ++
[
  show_int(2, d) ++ " | " ++
  join(" | ", [
    if card(TURNOS) = 2 then
      (if fix(x[p,d,1]) = 1 then "D" else "·" endif) ++
      (if fix(x[p,d,2]) = 1 then "N" else "·" endif) ++
      " (" ++ show_int(2, fix(sum(t in TURNOS)(
        puntajes[p,d,t] * x[p,d,t]))) ++ ")"
    else
      (if fix(x[p,d,1]) = 1 then "M" else "·" endif) ++
      (if fix(x[p,d,2]) = 1 then "T" else "·" endif) ++
      (if fix(x[p,d,3]) = 1 then "N" else "·" endif) ++
      " (" ++ show_int(2, fix(sum(t in TURNOS)(
        puntajes[p,d,t] * x[p,d,t]))) ++ ")"
    endif
    | p in PERSONAS
  ]) ++ " | " ++
  join(" ", ["T" ++ show(t) ++ ":" ++ show(demanda[d,t]) | t in TURNOS]) ++ "\n"
  | d in DIAS
] ++ [
  "\n======================================================================\n",
  "RESUMEN POR PERSONA:\n",
  concat([
    "P" ++ show(p) ++ ": " ++
    show_int(2, fix(sum(d in DIAS, t in TURNOS)(x[p,d,t]))) ++ " turnos | " ++
    show(fix(sum(w in SEMANAS)(y[p,w]))) ++ " findes | " ++
    "Score: " ++ show_int(3, fix(sum(d in DIAS, t in TURNOS)(
      puntajes[p,d,t] * x[p,d,t]))) ++ "\n"
    | p in PERSONAS
  ]),
  "\nDemanda total: " ++ show(sum(d in DIAS, t in TURNOS)(demanda[d,t])) ++ " turnos\n"
];
