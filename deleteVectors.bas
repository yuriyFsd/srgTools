Option Explicit

Sub Main()
	Dim femap As femap.model
    Set femap = feFemap()
    
    Dim outSetIdSet As femap.Set, vecIdSet As femap.Set
    
    Set outSetIdSet = femap.feSet
    Set vecIdSet = femap.feSet
   
    Dim title As String, nBaseOutputSetID As Long, nPreCheckedSetSetID As Long, nPreCheckedVectorSetID As Long, limitOutputType as long, limitComplex as long, limitToEntity as long, includeCorner as long, rc as long
	title = "Select outputsets & vectors to delete"
    nBaseOutputSetID  = 0 'active outset as default
    nPreCheckedSetSetID = 0
    nPreCheckedVectorSetID = 0
    nPreCheckedVectorSetID = 0 'All
	limitOutputType = 0
    limitComplex = 4 'any
    limitToEntity = 0
    includeCorner = True
    Dim pOutputSets As femap.Set, pOutputVecs As femap.Set
    femap.feSelectOutput2V2(title, nBaseOutputSetID, nPreCheckedSetSetID, nPreCheckedVectorSetID, limitOutputType, limitComplex, limitToEntity, includeCorner, pOutputSets, pOutputVecs)
    
    'App.Pref_FastOutputDelete = 1
     rc = femap.feDeleteOutput2V2(pOutputSets.id, pOutputVecs.id)
	 if (rc = -1) then
		femap.feAppMessageBox(0, "Deleted")
	 Else
		femap.feAppMessageBox(0, "Can't delete vectors")
	 End If
End Sub

