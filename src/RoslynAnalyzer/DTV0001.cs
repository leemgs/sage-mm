using System.Collections.Immutable;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.Diagnostics;

namespace SageMM.Analyzers;

[DiagnosticAnalyzer(LanguageNames.CSharp)]
public class DTV0001_ValueTypeSuggestion : DiagnosticAnalyzer
{
    public const string Id = "DTV0001";
    private static readonly DiagnosticDescriptor Rule = new(
        Id,
        "Consider struct for short-lived POD wrapper",
        "Type '{0}' appears to be a short-lived POD wrapper; consider converting to 'struct' to reduce heap churn",
        "Performance",
        DiagnosticSeverity.Info,
        isEnabledByDefault: true);

    public override ImmutableArray<DiagnosticDescriptor> SupportedDiagnostics => ImmutableArray.Create(Rule);

    public override void Initialize(AnalysisContext context)
    {
        context.ConfigureGeneratedCodeAnalysis(GeneratedCodeAnalysisFlags.None);
        context.EnableConcurrentExecution();
        context.RegisterSymbolAction(AnalyzeNamedType, SymbolKind.NamedType);
    }

    private static void AnalyzeNamedType(SymbolAnalysisContext ctx)
    {
        var type = (INamedTypeSymbol)ctx.Symbol;
        if (type.TypeKind != TypeKind.Class) return;
        if (type.Name.EndsWith("Handle") || type.Name.Contains("Vector") || type.Name.Contains("Color"))
        {
            // Heuristic: auto-properties with primitive fields only
            foreach (var f in type.GetMembers())
            {
                if (f is IPropertySymbol p && p.Type.SpecialType != SpecialType.None)
                {
                    var diag = Diagnostic.Create(Rule, type.Locations[0], type.Name);
                    ctx.ReportDiagnostic(diag);
                    break;
                }
            }
        }
    }
}
