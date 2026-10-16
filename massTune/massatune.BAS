Sub Main
	Dim App As femap.model
	Set App = GetObject(,"femap.model")

    Dim Leng As Double
    Dim area As Double
    Dim volume As Double
    Dim structMass As Double
    Dim nonstruct As Double
    Dim totalMass As Double
    Dim structCG As Variant
    Dim nonstructCG As Variant
    Dim totalCG As Variant
    Dim inertia As Variant
    Dim inertiaCG As Variant

   Dim MassaTune As Double

    Dim CogFin(2) As Double
    Dim MassaFin As Double
	
	Dim elm As Object
	Set elm=App.feElem


    Dim nd As Object
    Set nd=App.feNode

     Dim Prop As Object
    Set Prop =App.feProp

    CogFin(0) = 14300

    CogFin(1) = 0

    CogFin(2) = 7770

    MassaFin = 582650

    Dim ElemSet As Object
    Set ElemSet = App.feSet

  Dim feText As femap.text
 Set feText = App.feText
  ' elementen selecteren
  j = ElemSet.Select(8, Clear, "Selecteer elementen.")


  App.feMeasureMeshMassProp(ElemSet.ID, 0, True, False, Leng, area, volume, structMass, nonstruct, totalMass, structCG, nonstructCG, totalCG, inertia, inertiaCG )


  nd.Get(1)

    MassaTune = MassaFin - totalMass
    nd.x =  (MassaFin*CogFin(0)  -  totalMass*totalCG(0) ) /MassaTune
    nd.y =  (MassaFin*CogFin(1)  -  totalMass*totalCG(1) ) /MassaTune
    nd.z =  (MassaFin*CogFin(2)  -  totalMass*totalCG(2) ) /MassaTune

  ' nodeID = nd.NextEmptyID
  nodeID = 111222333

  nd.Put(nodeID)


  'prID = Prop.NextEmptyID
  prID = 3000
  'Prop.Get(2007)
  Prop.title = "massatune"
  Prop.type = 27
  Prop.pval(7) = MassaTune
  Prop.pval(11) = MassaTune
  Prop.pval(12) = MassaTune
  
  Prop.Put(prID)

  ElmID =111222333
  elm.ID = ElmID

  elm.Node(0) = nodeID

  elm.propID= prID
  elm.type = 27
  elm.topology=9

  elm.Put(101202303)


  feText.ModelPosition = True
  feText.DrawPointer = True
  feText.AllViews = True
  feText.DrawBorder = True
  feText.BackColor = FCL_YELLOW

  'positie van de tekstbox aangeven
   feText.TextPosition(0) = totalCG(0)
   feText.TextPosition(1) = totalCG(1)
   feText.TextPosition(2) = totalCG(2) + 10

   'positie van de pijl bij de tekstbox aangeven
   feText.PointerPosition(0) = totalCG(0)
   feText.PointerPosition(1) = totalCG(1)
   feText.PointerPosition(2) = totalCG(2)


   totalCG(0)=  Round(totalCG(0),2)
   totalCG(1)=  Round(totalCG(1),2)
   totalCG(2)=  Round(totalCG(2),2)

  feText.text = ("COG" & vbNewLine& " x = " & totalCG(0) & vbNewLine & "y = " & totalCG(1) & vbNewLine & "z = " & totalCG(2))

  feText.Put(1234)

   App.feViewRegenerate(0)

End Sub
