param(
    [Parameter(Mandatory = $true)]
    [string]$InputPath,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath,

    [double]$Scale = 1.5
)

Add-Type -AssemblyName System.Drawing

function Get-StyleValue {
    param([string]$Style, [string]$Name, [string]$Default = "")
    $match = [regex]::Match($Style, "(?:^|;)$([regex]::Escape($Name))=([^;]+)")
    if ($match.Success) { return $match.Groups[1].Value }
    return $Default
}

function Get-Colour {
    param([string]$Hex, [System.Drawing.Color]$Default)
    if ([string]::IsNullOrWhiteSpace($Hex) -or $Hex -eq "none") { return $Default }
    try { return [System.Drawing.ColorTranslator]::FromHtml($Hex) } catch { return $Default }
}

function Get-PlainText {
    param([string]$Value)
    if ($null -eq $Value) { return "" }
    $text = [System.Net.WebUtility]::HtmlDecode($Value)
    $text = [regex]::Replace($text, "(?i)<br\s*/?>", "`n")
    $text = [regex]::Replace($text, "<[^>]+>", "")
    return [System.Net.WebUtility]::HtmlDecode($text)
}

function Get-RoundedPath {
    param([System.Drawing.RectangleF]$Rectangle, [single]$Radius)
    $path = New-Object System.Drawing.Drawing2D.GraphicsPath
    $diameter = $Radius * 2
    $arc = New-Object System.Drawing.RectangleF($Rectangle.X, $Rectangle.Y, $diameter, $diameter)
    $path.AddArc($arc, 180, 90)
    $arc.X = $Rectangle.Right - $diameter
    $path.AddArc($arc, 270, 90)
    $arc.Y = $Rectangle.Bottom - $diameter
    $path.AddArc($arc, 0, 90)
    $arc.X = $Rectangle.Left
    $path.AddArc($arc, 90, 90)
    $path.CloseFigure()
    return $path
}

function Get-ConnectionPoints {
    param([System.Drawing.RectangleF]$Source, [System.Drawing.RectangleF]$Target)
    $sx = $Source.X + ($Source.Width / 2)
    $sy = $Source.Y + ($Source.Height / 2)
    $tx = $Target.X + ($Target.Width / 2)
    $ty = $Target.Y + ($Target.Height / 2)
    $dx = $tx - $sx
    $dy = $ty - $sy
    if ([math]::Abs($dx) -ge [math]::Abs($dy)) {
        if ($dx -ge 0) { $sx = $Source.Right; $tx = $Target.Left }
        else { $sx = $Source.Left; $tx = $Target.Right }
    } else {
        if ($dy -ge 0) { $sy = $Source.Bottom; $ty = $Target.Top }
        else { $sy = $Source.Top; $ty = $Target.Bottom }
    }
    return @([System.Drawing.PointF]::new($sx, $sy), [System.Drawing.PointF]::new($tx, $ty))
}

function Draw-ArrowHead {
    param(
        [System.Drawing.Graphics]$Graphics,
        [System.Drawing.Pen]$Pen,
        [System.Drawing.PointF]$From,
        [System.Drawing.PointF]$To
    )
    $angle = [math]::Atan2($To.Y - $From.Y, $To.X - $From.X)
    $size = 10.0
    $left = [System.Drawing.PointF]::new(
        $To.X - $size * [math]::Cos($angle - 0.45),
        $To.Y - $size * [math]::Sin($angle - 0.45)
    )
    $right = [System.Drawing.PointF]::new(
        $To.X - $size * [math]::Cos($angle + 0.45),
        $To.Y - $size * [math]::Sin($angle + 0.45)
    )
    $brush = New-Object System.Drawing.SolidBrush($Pen.Color)
    $Graphics.FillPolygon($brush, @($To, $left, $right))
    $brush.Dispose()
}

[xml]$document = Get-Content -LiteralPath $InputPath -Raw
$model = $document.mxfile.diagram.mxGraphModel
$cells = @($model.root.mxCell)
$pageWidth = [int]$model.pageWidth
$pageHeight = [int]$model.pageHeight
if ($pageWidth -le 0) { $pageWidth = 1200 }
if ($pageHeight -le 0) { $pageHeight = 850 }

$bounds = @{}
foreach ($cell in $cells) {
    if ($cell.vertex -eq "1" -and $null -ne $cell.mxGeometry) {
        $geometry = $cell.mxGeometry
        $bounds[[string]$cell.id] = [System.Drawing.RectangleF]::new(
            [single]$geometry.x,
            [single]$geometry.y,
            [single]$geometry.width,
            [single]$geometry.height
        )
    }
}

$bitmap = New-Object System.Drawing.Bitmap([int]($pageWidth * $Scale), [int]($pageHeight * $Scale))
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.Clear([System.Drawing.Color]::White)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
$graphics.ScaleTransform([single]$Scale, [single]$Scale)

$containerIds = @{}
foreach ($cell in $cells) {
    if ($cell.vertex -ne "1" -or -not $bounds.ContainsKey([string]$cell.id)) { continue }
    $rectangle = $bounds[[string]$cell.id]
    $style = [string]$cell.style
    $shape = Get-StyleValue $style "shape"
    $isText = $style.StartsWith("text;")
    $isContainer = $style.Contains("swimlane") -or (
        -not $isText -and
        $shape -notin @("umlActor", "component", "cylinder3", "startState", "endState") -and
        -not $style.Contains("ellipse") -and
        -not $style.Contains("rhombus") -and
        $rectangle.Width -ge 350 -and
        $rectangle.Height -ge 300
    )
    if (-not $isContainer) { continue }

    $containerIds[[string]$cell.id] = $true
    $fillHex = Get-StyleValue $style "fillColor" "#ffffff"
    $strokeHex = Get-StyleValue $style "strokeColor" "#4b5563"
    $fill = Get-Colour $fillHex ([System.Drawing.Color]::White)
    $stroke = Get-Colour $strokeHex ([System.Drawing.Color]::FromArgb(75, 85, 99))
    $brush = New-Object System.Drawing.SolidBrush($fill)
    $pen = New-Object System.Drawing.Pen($stroke, 1.7)

    if ($shape -eq "cube") {
        $offset = 12
        $front = [System.Drawing.RectangleF]::new($rectangle.X, $rectangle.Y + $offset, $rectangle.Width - $offset, $rectangle.Height - $offset)
        $graphics.FillRectangle($brush, $front)
        $graphics.DrawRectangle($pen, $front.X, $front.Y, $front.Width, $front.Height)
        $graphics.DrawLine($pen, $front.X, $front.Y, $front.X + $offset, $rectangle.Y)
        $graphics.DrawLine($pen, $front.Right, $front.Y, $rectangle.Right, $rectangle.Y)
        $graphics.DrawLine($pen, $front.X + $offset, $rectangle.Y, $rectangle.Right, $rectangle.Y)
        $graphics.DrawLine($pen, $front.Right, $front.Y, $rectangle.Right, $rectangle.Bottom - $offset)
    } else {
        $graphics.FillRectangle($brush, $rectangle)
        $graphics.DrawRectangle($pen, $rectangle.X, $rectangle.Y, $rectangle.Width, $rectangle.Height)
    }

    $labelHeight = 45.0
    if ($style.Contains("swimlane")) {
        $labelHeight = [single](Get-StyleValue $style "startSize" "35")
        $headerColour = Get-Colour (Get-StyleValue $style "swimlaneFillColor" $fillHex) $fill
        $headerBrush = New-Object System.Drawing.SolidBrush($headerColour)
        $graphics.FillRectangle($headerBrush, $rectangle.X, $rectangle.Y, $rectangle.Width, $labelHeight)
        $graphics.DrawLine($pen, $rectangle.X, $rectangle.Y + $labelHeight, $rectangle.Right, $rectangle.Y + $labelHeight)
        $headerBrush.Dispose()
    }

    $label = Get-PlainText ([string]$cell.value)
    if (-not [string]::IsNullOrWhiteSpace($label)) {
        $fontSize = [single](Get-StyleValue $style "fontSize" "13")
        $font = New-Object System.Drawing.Font("Segoe UI", $fontSize, [System.Drawing.FontStyle]::Bold)
        $format = New-Object System.Drawing.StringFormat
        $format.Alignment = [System.Drawing.StringAlignment]::Center
        $format.LineAlignment = [System.Drawing.StringAlignment]::Center
        $textRect = [System.Drawing.RectangleF]::new($rectangle.X + 8, $rectangle.Y, $rectangle.Width - 16, $labelHeight)
        $graphics.DrawString($label, $font, [System.Drawing.Brushes]::Black, $textRect, $format)
        $format.Dispose()
        $font.Dispose()
    }
    $brush.Dispose()
    $pen.Dispose()
}

foreach ($cell in $cells) {
    if ($cell.edge -ne "1") { continue }
    $style = [string]$cell.style
    $pen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(75, 85, 99), 1.6)
    if ((Get-StyleValue $style "dashed") -eq "1") {
        $pen.DashStyle = [System.Drawing.Drawing2D.DashStyle]::Dash
    }

    $start = $null
    $end = $null
    $geometry = $cell.mxGeometry
    $points = @($geometry.mxPoint)
    $sourcePoint = $points | Where-Object { $_.as -eq "sourcePoint" } | Select-Object -First 1
    $targetPoint = $points | Where-Object { $_.as -eq "targetPoint" } | Select-Object -First 1

    if ($null -ne $sourcePoint) {
        $start = [System.Drawing.PointF]::new([single]$sourcePoint.x, [single]$sourcePoint.y)
    } elseif ($bounds.ContainsKey([string]$cell.source)) {
        $sourceBounds = $bounds[[string]$cell.source]
        $start = [System.Drawing.PointF]::new(
            $sourceBounds.X + ($sourceBounds.Width / 2),
            $sourceBounds.Bottom
        )
    }

    if ($null -ne $targetPoint) {
        $end = [System.Drawing.PointF]::new([single]$targetPoint.x, [single]$targetPoint.y)
    }

    if ($null -eq $end -and $bounds.ContainsKey([string]$cell.source) -and $bounds.ContainsKey([string]$cell.target)) {
        $connection = Get-ConnectionPoints $bounds[[string]$cell.source] $bounds[[string]$cell.target]
        $start = $connection[0]
        $end = $connection[1]
    } elseif ($null -eq $start -and $bounds.ContainsKey([string]$cell.source)) {
        $sourceBounds = $bounds[[string]$cell.source]
        $start = [System.Drawing.PointF]::new($sourceBounds.X + ($sourceBounds.Width / 2), $sourceBounds.Bottom)
    }

    if ($null -ne $start -and $null -ne $end) {
        $graphics.DrawLine($pen, $start, $end)
        if ((Get-StyleValue $style "endArrow" "block") -ne "none") {
            Draw-ArrowHead $graphics $pen $start $end
        }
        $label = Get-PlainText ([string]$cell.value)
        if (-not [string]::IsNullOrWhiteSpace($label)) {
            $font = New-Object System.Drawing.Font("Segoe UI", 9)
            $labelSize = $graphics.MeasureString($label, $font)
            $mx = (($start.X + $end.X) / 2) - ($labelSize.Width / 2)
            $my = (($start.Y + $end.Y) / 2) - $labelSize.Height - 3
            $background = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
            $graphics.FillRectangle($background, $mx - 2, $my, $labelSize.Width + 4, $labelSize.Height)
            $graphics.DrawString($label, $font, [System.Drawing.Brushes]::DimGray, $mx, $my)
            $background.Dispose()
            $font.Dispose()
        }
    }
    $pen.Dispose()
}

foreach ($cell in $cells) {
    if ($cell.vertex -ne "1" -or -not $bounds.ContainsKey([string]$cell.id)) { continue }
    if ($containerIds.ContainsKey([string]$cell.id)) { continue }
    $rectangle = $bounds[[string]$cell.id]
    $style = [string]$cell.style
    $shape = Get-StyleValue $style "shape"
    $isText = $style.StartsWith("text;")
    $fillHex = Get-StyleValue $style "fillColor" "#ffffff"
    $strokeHex = Get-StyleValue $style "strokeColor" "#4b5563"
    $fill = Get-Colour $fillHex ([System.Drawing.Color]::White)
    $stroke = Get-Colour $strokeHex ([System.Drawing.Color]::FromArgb(75, 85, 99))
    $brush = New-Object System.Drawing.SolidBrush($fill)
    $pen = New-Object System.Drawing.Pen($stroke, 1.7)

    if (-not $isText) {
        if ($shape -eq "umlActor") {
            $centreX = $rectangle.X + ($rectangle.Width / 2)
            $headY = $rectangle.Y + 12
            $graphics.DrawEllipse($pen, $centreX - 14, $headY, 28, 28)
            $graphics.DrawLine($pen, $centreX, $headY + 28, $centreX, $rectangle.Y + 78)
            $graphics.DrawLine($pen, $centreX - 28, $rectangle.Y + 52, $centreX + 28, $rectangle.Y + 52)
            $graphics.DrawLine($pen, $centreX, $rectangle.Y + 78, $centreX - 26, $rectangle.Y + 105)
            $graphics.DrawLine($pen, $centreX, $rectangle.Y + 78, $centreX + 26, $rectangle.Y + 105)
        } elseif ($shape -eq "startState") {
            $graphics.FillEllipse([System.Drawing.Brushes]::Black, $rectangle)
        } elseif ($shape -eq "endState") {
            $graphics.DrawEllipse((New-Object System.Drawing.Pen([System.Drawing.Color]::Black, 2)), $rectangle)
            $inner = [System.Drawing.RectangleF]::new($rectangle.X + 7, $rectangle.Y + 7, $rectangle.Width - 14, $rectangle.Height - 14)
            $graphics.FillEllipse([System.Drawing.Brushes]::Black, $inner)
        } elseif ($shape -eq "cylinder3") {
            $graphics.FillRectangle($brush, $rectangle.X, $rectangle.Y + 10, $rectangle.Width, $rectangle.Height - 20)
            $graphics.DrawRectangle($pen, $rectangle.X, $rectangle.Y + 10, $rectangle.Width, $rectangle.Height - 20)
            $graphics.FillEllipse($brush, $rectangle.X, $rectangle.Y, $rectangle.Width, 22)
            $graphics.DrawEllipse($pen, $rectangle.X, $rectangle.Y, $rectangle.Width, 22)
            $graphics.DrawArc($pen, $rectangle.X, $rectangle.Bottom - 22, $rectangle.Width, 22, 0, 180)
        } elseif ($shape -eq "cube") {
            $offset = 12
            $front = [System.Drawing.RectangleF]::new($rectangle.X, $rectangle.Y + $offset, $rectangle.Width - $offset, $rectangle.Height - $offset)
            $graphics.FillRectangle($brush, $front)
            $graphics.DrawRectangle($pen, $front.X, $front.Y, $front.Width, $front.Height)
            $graphics.DrawLine($pen, $front.X, $front.Y, $front.X + $offset, $rectangle.Y)
            $graphics.DrawLine($pen, $front.Right, $front.Y, $rectangle.Right, $rectangle.Y)
            $graphics.DrawLine($pen, $front.X + $offset, $rectangle.Y, $rectangle.Right, $rectangle.Y)
            $graphics.DrawLine($pen, $front.Right, $front.Y, $rectangle.Right, $rectangle.Bottom - $offset)
        } elseif ($style.Contains("rhombus")) {
            $diamond = @(
                [System.Drawing.PointF]::new($rectangle.X + $rectangle.Width / 2, $rectangle.Y),
                [System.Drawing.PointF]::new($rectangle.Right, $rectangle.Y + $rectangle.Height / 2),
                [System.Drawing.PointF]::new($rectangle.X + $rectangle.Width / 2, $rectangle.Bottom),
                [System.Drawing.PointF]::new($rectangle.X, $rectangle.Y + $rectangle.Height / 2)
            )
            $graphics.FillPolygon($brush, $diamond)
            $graphics.DrawPolygon($pen, $diamond)
        } elseif ($style.Contains("ellipse")) {
            $graphics.FillEllipse($brush, $rectangle)
            $graphics.DrawEllipse($pen, $rectangle)
        } elseif ($style.Contains("swimlane")) {
            $graphics.FillRectangle($brush, $rectangle)
            $graphics.DrawRectangle($pen, $rectangle.X, $rectangle.Y, $rectangle.Width, $rectangle.Height)
            $headerHeight = [single](Get-StyleValue $style "startSize" "35")
            $headerColour = Get-Colour (Get-StyleValue $style "swimlaneFillColor" $fillHex) $fill
            $headerBrush = New-Object System.Drawing.SolidBrush($headerColour)
            $graphics.FillRectangle($headerBrush, $rectangle.X, $rectangle.Y, $rectangle.Width, $headerHeight)
            $graphics.DrawLine($pen, $rectangle.X, $rectangle.Y + $headerHeight, $rectangle.Right, $rectangle.Y + $headerHeight)
            $headerBrush.Dispose()
        } elseif ((Get-StyleValue $style "rounded") -eq "1") {
            $path = Get-RoundedPath $rectangle 10
            $graphics.FillPath($brush, $path)
            $graphics.DrawPath($pen, $path)
            $path.Dispose()
        } else {
            $graphics.FillRectangle($brush, $rectangle)
            $graphics.DrawRectangle($pen, $rectangle.X, $rectangle.Y, $rectangle.Width, $rectangle.Height)
            if ($shape -eq "component") {
                $graphics.FillRectangle($brush, $rectangle.X - 5, $rectangle.Y + 16, 18, 12)
                $graphics.DrawRectangle($pen, $rectangle.X - 5, $rectangle.Y + 16, 18, 12)
                $graphics.FillRectangle($brush, $rectangle.X - 5, $rectangle.Y + 38, 18, 12)
                $graphics.DrawRectangle($pen, $rectangle.X - 5, $rectangle.Y + 38, 18, 12)
            }
        }
    }

    $label = Get-PlainText ([string]$cell.value)
    if (-not [string]::IsNullOrWhiteSpace($label) -and $shape -ne "startState" -and $shape -ne "endState") {
        $fontSize = [single](Get-StyleValue $style "fontSize" "12")
        $fontStyle = [System.Drawing.FontStyle]::Regular
        if ((Get-StyleValue $style "fontStyle") -eq "1") { $fontStyle = [System.Drawing.FontStyle]::Bold }
        $font = New-Object System.Drawing.Font("Segoe UI", $fontSize, $fontStyle)
        $format = New-Object System.Drawing.StringFormat
        $format.Alignment = if ((Get-StyleValue $style "align") -eq "left") { [System.Drawing.StringAlignment]::Near } else { [System.Drawing.StringAlignment]::Center }
        $format.LineAlignment = [System.Drawing.StringAlignment]::Center
        $textRect = $rectangle
        if ($style.Contains("swimlane")) {
            $headerHeight = [single](Get-StyleValue $style "startSize" "35")
            $textRect = [System.Drawing.RectangleF]::new($rectangle.X + 5, $rectangle.Y, $rectangle.Width - 10, $headerHeight)
        } elseif ($shape -eq "umlActor") {
            $textRect = [System.Drawing.RectangleF]::new($rectangle.X - 20, $rectangle.Bottom - 25, $rectangle.Width + 40, 45)
        } elseif ((Get-StyleValue $style "align") -eq "left") {
            $textRect = [System.Drawing.RectangleF]::new($rectangle.X + 6, $rectangle.Y, $rectangle.Width - 12, $rectangle.Height)
        }
        $graphics.DrawString($label, $font, [System.Drawing.Brushes]::Black, $textRect, $format)
        $format.Dispose()
        $font.Dispose()
    }
    $brush.Dispose()
    $pen.Dispose()
}

$outputDirectory = Split-Path -Parent $OutputPath
if (-not (Test-Path -LiteralPath $outputDirectory)) {
    New-Item -ItemType Directory -Path $outputDirectory | Out-Null
}
$bitmap.Save($OutputPath, [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$bitmap.Dispose()
Write-Output "Rendered $InputPath to $OutputPath"
