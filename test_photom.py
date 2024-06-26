from io import BytesIO

import matplotlib
import unittest
from PIL import Image
from numpy import dtype

from MSPhotomAnalysis import *


class TestPhotometryFunctions(unittest.TestCase):

    def test_datetonum(self):
        self.assertEqual(datetonum('01-00-00'), 40)
        self.assertEqual(datetonum('01-01-00'), 41)
        self.assertEqual(datetonum('01-01-01'), 541)
        #The following are grayed out because we currently do not create an error when somebody enters a date wrong
        #self.assertFalse(datetonum('01-32-01'))
        #self.assertFalse(datetonum('01-01-2024'))
        #self.assertFalse(datetonum('13-01-01'))

    def test_numtodate(self):
        #Tests the bidirectionality of conversion
        self.assertEqual(numtodate(40), '01-00-00')
        self.assertEqual(numtodate(41), '01-01-00')
        self.assertEqual(numtodate(541), '01-01-01')

    def test_npy_circlemask(self):
        #General Test to ensure the mask is properly circular
        mask = npy_circlemask(5, 5, 2, 2, 2)
        expected_mask = np.array([
            [0, 0, 1, 0, 0],
            [0, 1, 1, 1, 0],
            [1, 1, 1, 1, 1],
            [0, 1, 1, 1, 0],
            [0, 0, 1, 0, 0]], dtype = bool)
        self.assertTrue(np.array_equal(mask, expected_mask))
        #Ensures only the pixel selected is accounted for with a radius of zero
        mask = npy_circlemask(5, 5, 2, 2, 0)
        expected_mask = np.array([
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0]], dtype = bool)
        self.assertTrue(np.array_equal(mask, expected_mask))
        #Testing that the mask works properly if put on a corner
        mask = npy_circlemask(5, 5, 0, 0, 2)
        expected_mask = np.array([
            [1, 1, 1, 0, 0],
            [1, 1, 0, 0, 0],
            [1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0]], dtype = bool)
        self.assertTrue(np.array_equal(mask, expected_mask))

        #Ensures entire array will be filled if the radius is large enough
        mask = npy_circlemask(5, 5, 2, 2, 100)
        expected_mask = np.array([
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1]], dtype=bool)


    def test_photomimageprocess(self, p = 200):
        #Fake directory
        directory = 'test_images'
        os.makedirs(directory, exist_ok=True)
        imgprefix = 'test_img'

        img = Image.fromarray(np.ones((5, 5), dtype=np.uint8) * p)
        for i in range(5):
            img.save(os.path.join(directory, f"{imgprefix}0_{i + 1}.tif"))

        #Testing Mask
        masks = [np.ones((5, 5), dtype=bool)]

        #Running the function to calculate trace values
        traces = photomimageprocess(directory, imgprefix, masks)

        #Testing if it properly averages pixel values
        for trace in traces:
            self.assertTrue(np.all(trace == p))

        #Delete Images
        for i in range(5):
            os.remove(os.path.join(directory, f"{imgprefix}0_{i+1}.tif"))
        os.rmdir(directory)

    #Tests other values(min and max)
    def test_photon_other_values(self):
        self.test_photomimageprocess(p=0)
        self.test_photomimageprocess(p=255)

    def test_subtractbackgroundsignal(self):
        #Tests if typical operations are done correctly
        traces = [np.array([10, 10, 10]), np.array([20, 20, 20]), np.array([30, 30, 30]) ]
        result = subtractbackgroundsignal(traces)
        expected = [np.array([10, 10, 10]), np.array([20, 20, 20])]
        #For loop is for multiple array comparisons
        for res, exp in zip(result, expected):
            self.assertTrue(np.array_equal(res, exp))

        #Tests if it can subtract equivalent traces
        traces = [np.array([10, 10, 10]), np.array([10, 10, 10])]
        result = subtractbackgroundsignal(traces)
        expected = [np.array([0, 0, 0])]
        self.assertTrue(np.array_equal(result, expected))

        #Tests atypical(negative) Data Note:Should probably in the future assert a warning about the images
        traces = [np.array([20, 20, 20]), np.array([10, 10, 10]), ]
        result = subtractbackgroundsignal(traces)
        expected = [np.array([-10, -10, -10]), ]
        self.assertTrue(np.array_equal(result, expected))

    def test_splittraces(self):
        traces = [np.array([1, 2, 3, 4, 5, 6])]
        channels = 2
        result = splittraces(traces, channels)
        expected = [np.array([1, 3, 5]), np.array([2, 4, 6])]
        for res, exp in zip(result, expected):
            self.assertTrue(np.array_equal(res, exp))


        traces = [np.array([1, 2, 3, 4, 5, 6, 7])]
        channels = 2
        result = splittraces(traces, channels)
        expected = [np.array([1, 3, 5, 7]), np.array([2, 4, 6])]
        for res, exp in zip(result, expected):
            self.assertTrue(np.array_equal(res, exp))

        channels = 5
        result = splittraces(traces, channels)
        expected = [np.array([1, 6]), np.array([2, 7]), np.array([3,]), np.array([4,]), np.array([5,])]
        for res, exp in zip(result, expected):
            self.assertTrue(np.array_equal(res, exp))

    def test_reshapetraces(self):
        traces = [np.array([1, 2, 3, 4, 5, 6])]
        imgptrial = 3
        result = reshapetraces(traces, imgptrial)
        expected = [np.array([[1, 2, 3], [4, 5, 6]])]
        for res, exp in zip(result, expected):
            self.assertTrue(np.array_equal(res, exp))

        imgptrial = 6
        result = reshapetraces(traces, imgptrial)
        expected = [np.array([[1, 2, 3, 4, 5, 6]])]
        self.assertTrue(np.array_equal(result, expected))

        imgptrial = 10
        result = reshapetraces(traces, imgptrial)
        expected = [np.array([])]
        #Grayed out because the blank array in Reshapedtraces has other things defined
        #for res, exp in zip(result, expected):
            #self.assertTrue(np.array_equal(res, exp))

        traces = [np.array([1, 2, 3, 4, 5, 6, 7])]
        imgptrial = 3
        result = reshapetraces(traces, imgptrial)
        expected = [np.array([[1, 2, 3], [4, 5, 6]])]
        for res, exp in zip(result, expected):
            self.assertTrue(np.array_equal(res, exp))

    def test_loadimg(self):
        img = Image.fromarray(np.ones((5, 5), dtype=np.uint8) * 255)
        img.save("temp.tif", format="TIFF")
        loaded_img = loadimg("temp.tif")
        self.assertTrue(np.array_equal(loaded_img, np.ones((5, 5), dtype=np.uint8) * 255))
        os.remove("temp.tif")

if __name__ == '__main__':
    unittest.main()


