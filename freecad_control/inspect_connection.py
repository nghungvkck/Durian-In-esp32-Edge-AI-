result = {
    "version": list(App.Version()),
    "documents": {
        name: {"label": doc.Label, "objects": len(doc.Objects)}
        for name, doc in App.listDocuments().items()
    },
}
