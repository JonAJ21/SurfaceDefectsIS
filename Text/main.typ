#import "@preview/modern-g7-32:0.2.0": gost, abstract, appendixes

#show: gost.with(
  hide-title: true,
  city: "Москва",
  year: 2026,
)

// Реферат
#abstract(
  "информирование водителей",
  "дефекты дорожного покрытия",
  "акселерометр",
  "краудсорсинг",
  "мобильное приложение",
)[
  Выпускная квалификационная работа посвящена разработке системы информирования водителей о дефектах дорожного покрытия. В работе проведен анализ существующих методов мониторинга дорог, разработана архитектура системы, реализован прототип мобильного приложения и серверной части. Результаты тестирования подтверждают работоспособность предложенных решений.
]

#outline(title: "Содержание")

#include "sections/0-introduction.typ"
#include "sections/1-analysis.typ"
#include "sections/2-design.typ"
#include "sections/3-implementation.typ"
#include "sections/4-conclusion.typ"

#bibliography("ref.bib")

#show: appendixes
#include "appendices/appendix-a.typ"
#include "appendices/appendix-b.typ"